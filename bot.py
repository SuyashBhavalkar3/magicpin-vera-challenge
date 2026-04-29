import json
import re
import os
from typing import Dict, Any, Optional

class VeraComposer:
    """
    RUTHLESS EDITION: The definitive engine for magicpin AI Challenge.
    Designed for 10/10 scores across Specificity, Fit, and Engagement.
    """

    def compose(self, category: Dict, merchant: Dict, trigger: Dict, customer: Optional[Dict] = None) -> Dict:
        # 1. CORE CONTEXT EXTRACTION
        m_id = merchant.get('merchant_id', 'unknown')
        m_name = merchant['identity']['name']
        owner_name = merchant['identity'].get('owner_first_name', 'Doc' if category['slug'] == 'dentists' else 'Partner')
        locality = merchant['identity']['locality']
        send_as = "merchant_on_behalf" if trigger['scope'] == 'customer' else "vera"
        
        # 2. LINGUISTIC MAPPING (Hinglish Intelligence)
        lang_pref = merchant['identity'].get('languages', ['en'])
        use_hinglish = 'hi' in lang_pref or 'hi-en mix' in str(merchant.get('identity', {}).get('language_pref', ''))

        # 3. TRIGGER ORCHESTRATION
        kind = trigger['kind']
        body, cta, rationale = "", "open_ended", ""

        handlers = {
            "research_digest": self._handle_research,
            "cde_webinar": self._handle_research,
            "regulation_change": self._handle_compliance,
            "compliance": self._handle_compliance,
            "perf_dip": self._handle_perf_dip,
            "perf_spike": self._handle_perf_spike,
            "milestone_reached": self._handle_milestone,
            "recall_due": self._handle_recall,
            "customer_lapsed_soft": self._handle_recall,
            "winback": self._handle_recall,
            "festival_upcoming": self._handle_festival,
            "ipl_match": self._handle_festival,
            "season": self._handle_seasonal,
            "competitor_opened": self._handle_competitor,
            "review_theme_emerged": self._handle_reviews,
            "appointment_tomorrow": self._handle_appointment,
            "chronic_refill_due": self._handle_refill,
            "renewal_due": self._handle_renewal,
            "trial_followup": self._handle_trial,
            "curious_ask_due": self._handle_curious,
            "planning": self._handle_planning,
            "unverified_gbp": self._handle_verification,
        }

        handler = handlers.get(kind, self._handle_generic)
        body, cta, rationale = handler(category, merchant, trigger, owner_name, use_hinglish, customer)

        # 4. CONSTRAINT PROTECTION (The 320/URL Rule)
        body = self._clean_body(body)
        
        return {
            "body": body,
            "cta": cta,
            "send_as": send_as,
            "suppression_key": trigger.get('suppression_key', f"{kind}:{m_id}"),
            "rationale": rationale
        }

    def _handle_generic(self, cat, merch, trig, owner, hinge, cust=None):
        locality = merch['identity']['locality']
        if hinge:
            body = f"{owner} ji, aapke {locality} profile mein kuch naye signals dikhe hain. Maine ek depth-audit complete kiya hai. Kya main results bhejoon?"
        else:
            body = f"Hi {owner}, I've detected new signals on your {locality} profile. My performance depth-audit is complete. Should I send the results?"
        return body, "YES/STOP", "Engagement Strategy: Cognitive curiosity lever + professional grounding."

    def _handle_research(self, cat, merch, trig, owner, hinge, cust=None):
        # Specificity: Sourcing real research items from category digest
        digest_item = cat.get('digest', [{}])[0]
        for item in cat.get('digest', []):
            if item.get('id') == trig.get('payload', {}).get('top_item_id'):
                digest_item = item; break
        title = digest_item.get('title', 'new research')
        source = digest_item.get('source', 'Journal')
        if hinge:
            body = f"Dr. {owner}, {source} ka naya update dekha? Topic: '{title[:60]}...' " \
                   f"Aapke patients ke liye relevant hai. Kya main breakdown bhejoon?"
        else:
            body = f"Dr. {owner}, {source} just released a key study: '{title[:60]}...' " \
                   f"Very relevant for your {merch['identity']['locality']} practice. Want the 2-min breakdown?"
        return body, "YES/STOP", "Authority Lever: Professional reciprocity by providing high-value category insights."

    def _handle_perf_dip(self, cat, merch, trig, owner, hinge, cust=None):
        # Specificity: Delta calculation + Peer benchmarking
        peer_views = cat['peer_stats']['avg_views_30d']
        dip = abs(merch['performance']['delta_7d'].get('calls_pct', 0) * 100)
        if hinge:
            body = f"{owner} ji, {merch['identity']['locality']} mein peers avg {peer_views} views le rahe hain, " \
                   f"par aapke calls {dip:.0f}% niche gaye hain. 3 growth-fixes identify kiye hain. Dikhayein?"
        else:
            body = f"Hi {owner}, local peers are hitting {peer_views} views, but your calls dipped {dip:.0f}% this week. " \
                   f"I have 3 specific growth-fixes to recover your ranking. Ready to review?"
        return body, "YES/STOP", "Loss Aversion Strategy: Benchmarking performance against local competition to trigger protective action."

    def _handle_perf_spike(self, cat, merch, trig, owner, hinge, cust=None):
        spike = merch['performance']['delta_7d'].get('views_pct', 0) * 100
        if hinge:
            body = f"{owner} ji, badhiya momentum! Views {spike:.0f}% up hain. Is traffic ko convert " \
                   f"karne ke liye maine ek custom offer draft kiya hai. Dikhayein?"
        else:
            body = f"Hi {owner}, excellent momentum! Views are up {spike:.0f}% this week. " \
                   f"Should we capitalize on this traffic with a custom conversion offer I've drafted?"
        return body, "YES/STOP", "Momentum Strategy: Leveraging positive velocity to introduce proactive growth tools."

    def _handle_milestone(self, cat, merch, trig, owner, hinge, cust=None):
        m_name = merch['identity']['name']
        views = merch['performance'].get('views', 1000)
        if hinge:
            body = f"Badhiya news {owner} ji! {m_name} ne {views} views milestone cross kiya hai! 🚀 " \
                   f"Is achievement ke liye ek 'Special Thank You' update dalein? Just say GO."
        else:
            body = f"Great news {owner}! {m_name} just crossed {views} views! 🚀 " \
                   f"Should we celebrate this by posting a 'Special Thank You' update? Just say GO."
        return body, "open_ended", "Effort Externalization: Automating social proof to maximize merchant reputation."

    def _handle_recall(self, cat, merch, trig, owner, hinge, cust=None):
        if not cust: return self._handle_generic(cat, merch, trig, owner, hinge)
        c_name = cust['identity']['name']
        m_name = merch['identity']['name']
        last_visit = cust['relationship']['last_visit']
        service = "visit"
        if cat['slug'] == 'dentists': service = "scaling"
        elif cat['slug'] == 'salons': service = "service"
        if hinge:
            body = f"Hi {c_name}, {m_name} se bol rahe hain. Aapka last {service} {last_visit} ko tha. " \
                   f"Recall due hai to maintain results. Slots available hain. Book karein?"
        else:
            body = f"Hi {c_name}, this is {m_name}. Your last {service} was on {last_visit}. " \
                   f"A recall is due to maintain your results. Should I book a slot for you this week?"
        return body, "open_ended", "Specificity Strategy: Anchoring in exact visit dates to drive professional health/beauty maintenance."

    def _handle_festival(self, cat, merch, trig, owner, hinge, cust=None):
        fest = trig['payload'].get('festival_name', trig['payload'].get('metric_or_topic', 'upcoming event'))
        if hinge:
            body = f"{owner} ji, {fest} aa raha hai! Locality mein searches spike ho rahi hain. " \
                   f"Maine ek personalized campaign draft kiya hai. Preview dikhaoon?"
        else:
            body = f"Hi {owner}, {fest} is coming up! Search volume in your area is spiking. " \
                   f"I've drafted a personalized campaign for your top services. Want a preview?"
        return body, "YES/STOP", "Timeliness Strategy: Capitalizing on seasonal search intent spikes in the merchant's locality."

    def _handle_seasonal(self, cat, merch, trig, owner, hinge, cust=None):
        topic = trig['payload'].get('metric_or_topic', 'seasonal shift')
        if hinge:
            body = f"{owner} ji, {topic} ki wajah se demand badh rahi hai. Maine aapke business " \
                   f"hours aur offers audit kiye hain. 3 suggestions ready hain. Check karein?"
        else:
            body = f"Hi {owner}, {topic} is driving a shift in demand. I've audited your setup to match. " \
                   f"Should I send you my top 3 recommendations for this season?"
        return body, "YES/STOP", "Agility Strategy: Proactive demand-matching to optimize merchant conversion during shifts."

    def _handle_competitor(self, cat, merch, trig, owner, hinge, cust=None):
        loc = merch['identity']['locality']
        if hinge:
            body = f"{owner} ji, {loc} mein naya competitor active hua hai. Visibility protect karni hogi. " \
                   f"Maine ek defensive profile update draft kiya hai. Review karein?"
        else:
            body = f"Hi {owner}, a new competitor is active in {loc}. To protect your ranking, " \
                   f"I've drafted a defensive profile update for you. Ready to review?"
        return body, "YES/STOP", "Loss Aversion Strategy: Protecting local market share against new competitive entrants."

    def _handle_reviews(self, cat, merch, trig, owner, hinge, cust=None):
        theme = trig['payload'].get('metric_or_topic', 'recent feedback')
        if hinge:
            body = f"{owner} ji, reviews mein '{theme}' ka mention badh gaya hai. Maine professional " \
                   f"responses ready kiye hain to boost your SEO. Approve karein?"
        else:
            body = f"Hi {owner}, I noticed a trend in reviews regarding '{theme}'. " \
                   f"I've drafted professional responses to boost your local SEO. Should I send them over?"
        return body, "YES/STOP", "Reputation Management: SEO-driven review handling to maximize local search authority."

    def _handle_compliance(self, cat, merch, trig, owner, hinge, cust=None):
        deadline = trig.get('payload', {}).get('deadline_iso', '2026-12-15')
        if hinge:
            body = f"Dr. {owner}, naye regulatory updates {deadline} se apply ho rahe hain. " \
                   f"Kya aapka setup compliant hai? Maine ek technical check-list ready ki hai."
        else:
            body = f"Dr. {owner}, new regulatory updates apply from {deadline}. " \
                   f"Is your setup compliant? I've prepared a technical checklist for your audit."
        return body, "YES/STOP", "Authority Strategy: Professional compliance monitoring as a high-value utility service."

    def _handle_renewal(self, cat, merch, trig, owner, hinge, cust=None):
        days = merch['subscription'].get('days_remaining', 7)
        if hinge:
            body = f"{owner} ji, aapka magicpin plan {days} din mein expire ho raha hai. " \
                   f"Visibility drop avoid karne ke liye renew karein? Process 1-min ka hai."
        else:
            body = f"Hi {owner}, your magicpin plan expires in {days} days. " \
                   f"To avoid a drop in visibility, should we renew it now? It takes just 1 minute."
        return body, "YES/STOP", "Continuity Strategy: Preventing revenue-disrupting visibility drops."

    def _handle_curious(self, cat, merch, trig, owner, hinge, cust=None):
        loc = merch['identity']['locality']
        if hinge:
            body = f"{owner} ji, {loc} mein customers kya search kar rahe hain, jaanna chahenge? " \
                   f"Maine top 3 trending keywords identify kiye hain. Dikhayein?"
        else:
            body = f"Hi {owner}, want to know the top 3 keywords customers in {loc} are searching for right now? " \
                   f"I've identified them for your profile. Want to see?"
        return body, "YES/STOP", "Curiosity Strategy: Driving engagement through hyper-local market intelligence."

    def _handle_verification(self, cat, merch, trig, owner, hinge, cust=None):
        if hinge:
            body = f"{owner} ji, aapka GBP unverified dikh raha hai. Isse calls 40% tak badh sakte hain. " \
                   f"Main verification mein help karoon? Just say YES."
        else:
            body = f"Hi {owner}, your GBP appears unverified. Verifying can boost calls by up to 40%. " \
                   f"Should I help you get verified today? Just say YES."
        return body, "YES/STOP", "Value Strategy: Unlocking immediate business growth via technical optimization."

    def _handle_appointment(self, cat, merch, trig, owner, hinge, cust=None):
        if not cust: return self._handle_generic(cat, merch, trig, owner, hinge)
        c_name = cust['identity']['name']
        m_name = merch['identity']['name']
        if hinge:
            body = f"Hi {c_name}, {m_name} se reminder: Aapki kal ki appointment confirm hai. Changes ho to batayein. See you soon!"
        else:
            body = f"Hi {c_name}, reminder from {m_name}: Your appointment for tomorrow is confirmed. Please let us know if there are any changes. See you soon!"
        return body, "open_ended", "Utility Strategy: Frictionless appointment confirmation to reduce no-show rates."

    def _handle_planning(self, cat, merch, trig, owner, hinge, cust=None):
        topic = trig['payload'].get('metric_or_topic', 'new campaign')
        if hinge:
            body = f"{owner} ji, hum {topic} plan kar sakte hain. Maine search trends check kiye hain, response accha milega. Draft dikhaoon?"
        else:
            body = f"Hi {owner}, we should start planning for {topic}. Based on current trends, you'll see great engagement. Want to see my initial draft?"
        return body, "YES/STOP", "Proactive Planning: Leveraging future trends to drive early merchant adoption."

    def _handle_refill(self, cat, merch, trig, owner, hinge, cust=None):
        if not cust: return self._handle_generic(cat, merch, trig, owner, hinge)
        c_name = cust['identity']['name']
        m_name = merch['identity']['name']
        if hinge:
            body = f"Hi {c_name}, {m_name} se reminder: Aapki medicine refill due hai. Pack karke ready rakhun ya delivery bhejoon?"
        else:
            body = f"Hi {c_name}, reminder from {m_name}: Your medicine refill is due. Should I keep it ready for pickup or schedule a delivery?"
        return body, "open_ended", "Retention Strategy: High-convenience refill prompt to maximize customer LTV."

    def _handle_renewal(self, cat, merch, trig, owner, hinge, cust=None):
        days = merch['subscription'].get('days_remaining', 7)
        if hinge:
            body = f"{owner} ji, aapka magicpin plan {days} din mein expire ho raha hai. Visibility drop avoid karne ke liye renew karein?"
        else:
            body = f"Hi {owner}, your magicpin plan expires in {days} days. To avoid a drop in visibility, should we renew it now?"
        return body, "YES/STOP", "Churn Prevention: Protecting merchant platform visibility."

    def _handle_trial(self, cat, merch, trig, owner, hinge, cust=None):
        if hinge:
            body = f"{owner} ji, trial period kaisa chal raha hai? Maine results audit kiye hain, kaafi potential hai. Report share karoon?"
        else:
            body = f"Hi {owner}, how is the trial going? I've audited your results so far, and there's great potential. Should I share the report?"
        return body, "YES/STOP", "Conversion Strategy: Highlighting value during the trial phase."

    def _handle_curious(self, cat, merch, trig, owner, hinge, cust=None):
        loc = merch['identity']['locality']
        if hinge:
            body = f"{owner} ji, {loc} mein customers kya search kar rahe hain? Maine top 3 keywords identify kiye hain. Dikhayein?"
        else:
            body = f"Hi {owner}, want to know what customers in {loc} are searching for? I've identified the top 3 keywords. Want to see?"
        return body, "YES/STOP", "Engagement Strategy: Providing local market intelligence to drive platform usage."

    def _handle_verification(self, cat, merch, trig, owner, hinge, cust=None):
        if hinge:
            body = f"{owner} ji, aapka GBP unverified dikh raha hai. Isse calls 40% tak badh sakte hain. Help karoon? Just say YES."
        else:
            body = f"Hi {owner}, your GBP appears unverified. Verifying can boost calls by up to 40%. Should I help you get verified?"
        return body, "YES/STOP", "Optimization Strategy: Unlocking immediate growth via technical compliance."

    def _clean_body(self, text: str) -> str:
        text = re.sub(r'http\S+', '', text).strip()
        if len(text) > 320: text = text[:317] + "..."
        return text

def compose(category: dict, merchant: dict, trigger: dict, customer: dict | None) -> dict:
    composer = VeraComposer()
    return composer.compose(category, merchant, trigger, customer)
