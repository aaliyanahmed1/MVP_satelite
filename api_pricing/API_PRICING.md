# API Pricing & Usage Plan 

## APIs Required 

### 1. MapTiler API (Satellite Imagery)
- **Website:** [https://www.maptiler.com](https://www.maptiler.com)
- **Free Tier:** 100,000 requests/month
- **Pricing:** $0.10 per 1,000 extra requests
- **What it does:** Fetches satellite images for roof detection
- **Usage:** ~30 tiles per zipcode

### 2. Google Maps Geocoding API (Reverse Geocoding)
- **Website:** [https://developers.google.com/maps/documentation/geocoding](https://developers.google.com/maps/documentation/geocoding)
- **Free Tier:** 10,000 requests/month
- **Pricing:** $5 per 1,000 extra requests
- **What it does:** Converts coordinates to addresses
- **Usage:** 1 request per property

### 3. Tracerfy API (Property Owner Lookup)
- **Website:** [https://tracerfy.com](https://tracerfy.com)
- **Free Tier:** Contact for details (typically 100-1,000/month)
- **Pricing:** Contact for pricing (usually $0.10-0.50 per lookup)
- **What it does:** Finds property owner details from address
- **Usage:** 1 request per property

### 4. SendGrid API (Email Sending)
- **Website:** [https://sendgrid.com](https://sendgrid.com)
- **Free Tier:** 100 emails/day = 3,000 emails/month
- **Pricing:** $19.95/month for 50,000 emails
- **What it does:** Sends email notifications to property owners
- **Usage:** 1 email per damaged property

---

## Monthly Usage Scenarios

### Small Scale (FREE)
- **Zipcodes:** 100/month
- **Damaged Properties:** 200/month
- **MapTiler:** 3,000 requests ✅ (within 100K free limit)
- **Google Geocoding:** 200 requests ✅ (within 10K free limit)
- **Tracerfy:** 200 requests ⚠️ (check free tier)
- **SendGrid:** 200 emails ✅ (within 3K free limit)
- **Cost:** $0/month

### Medium Scale (Mostly FREE)
- **Zipcodes:** 500/month
- **Damaged Properties:** 1,000/month
- **MapTiler:** 15,000 requests ✅ (within 100K free limit)
- **Google Geocoding:** 1,000 requests ✅ (within 10K free limit)
- **Tracerfy:** 1,000 requests ⚠️ (may need paid plan)
- **SendGrid:** 1,000 emails ✅ (within 3K free limit)
- **Cost:** $0-50/month (depends on Tracerfy)

### Large Scale (PAID)
- **Zipcodes:** 2,000/month
- **Damaged Properties:** 5,000/month
- **MapTiler:** 60,000 requests ✅ (within 100K free limit)
- **Google Geocoding:** 5,000 requests ✅ (within 10K free limit)
- **Tracerfy:** 5,000 requests ❌ (needs paid plan)
- **SendGrid:** 5,000 emails ❌ (needs paid plan: $19.95/month)
- **Cost:** $50-200/month

---

## Free Tier Summary

| API | Free Tier Limit | What You Can Do |
|-----|----------------|-----------------|
| MapTiler | 100,000 requests/month | ~3,333 zipcodes/month |
| Google Geocoding | 10,000 requests/month | 10,000 properties/month |
| Tracerfy | Contact them | Usually 100-1,000/month |
| SendGrid | 3,000 emails/month | 3,000 property owners/month |

---

## Pricing Beyond Free Tier

1. **MapTiler:** $0.10 per 1,000 extra requests
2. **Google Geocoding:** $5 per 1,000 extra requests
3. **Tracerfy:** Contact for pricing
4. **SendGrid:** $19.95/month for 50,000 emails

---

## Key Limits

**Bottleneck:** Google Geocoding (10K/month) is the main limit. You can handle ~10,000 property lookups/month on free tier.

**SendGrid:** 100 emails/day hard limit on free tier.

**Recommendation:** Start with free tier (100 zipcodes/month, 200 properties/month) and scale up when needed.

