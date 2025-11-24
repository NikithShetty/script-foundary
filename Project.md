

## **AI Educational Script Generator**

***

### **1. CORE SYSTEM ARCHITECTURE**

Your solution should address three interconnected layers:

#### **Layer 1: Curriculum Intelligence**
- **CurricuLLM-AU API Integration**: Pull curriculum outcomes, year levels, and learning standards from the Australian curriculum
- **Misconception Database**: Link to documented common misconceptions for each topic (sourced from cognitive science research)
- **Learning Progression Maps**: Define prerequisite knowledge and conceptual sequencing

#### **Layer 2: Pedagogical Script Framework**
Embed these evidence-based techniques directly into script generation:

| Technique | Implementation in Script |
|-----------|------------------------|
| **Worked Examples** | Scene 1-2: Full solved problem with narration explaining each step (I Do) |
| **Faded Examples** | Scene 3-4: Partially solved problem, student fills gaps (We Do) |
| **Spaced Retrieval** | Built-in recall prompts: "What was [concept] we saw earlier?" |
| **Dual Encoding** | Visual descriptions + text narration working together (never redundant) |
| **Interleaving** | Script includes contrasting examples (this works / this doesn't work) |
| **Misconception Warnings** | Explicit text: "Common mistake: students think X, but actually Y" |

#### **Layer 3: Hallucination Prevention**
- **Retrieval-Augmented Generation (RAG)**: Ground all facts in verified sources (textbooks, curriculum docs, scientific papers)
- **Fact-Checking Gate**: Before finalizing, check outputs against curated educational databases
- **Confidence Scoring**: Flag claims with low confidence or unsourced statements
- **Cross-Reference Validation**: Verify numbers, dates, and scientific claims against multiple sources

***

### **2. USER WORKFLOW (Teacher-Friendly)**

```
Teacher Input
    ↓
"I need a script about photosynthesis for Year 5 
that shows why plants need light and water"
    ↓
System Processing:
  1. Parse curriculum alignment (Year 5 science outcomes)
  2. Retrieve known misconceptions about photosynthesis
  3. Pull verified facts from curriculum database
  4. Generate script with pedagogical scaffolding
    ↓
Output: Polished script with:
  • Scene-by-scene breakdown
  • Visual direction cues
  • Character/voice guidance
  • Accessibility captions
  • Animation direction
    ↓
Teacher Review & Edit
    ↓
Export as text (ready for video AI tool)
```

***

### **3. SCRIPT OUTPUT STRUCTURE**

Each generated script should follow this template:

```
EDUCATIONAL SCRIPT: [Topic]
Level: Year [N] | Duration: ~[minutes] | Curriculum Link: [Code]

SCENE 1: Hook & Context
[Visual description]
[Narration]
[Text overlay]
[Accessibility cue]

SCENE 2: Worked Example (I DO)
[Problem setup]
[Step-by-step solution with thinking aloud]
[Visual metaphor reinforcement]

SCENE 3: Faded Example (WE DO)
[Similar problem, partially solved]
[Student prompts for completion]
[Reveal solution with explanation]

SCENE 4: Key Concept Summary
[Spaced retrieval question]
[Common misconception addressed]
[Reinforcement visual]

SCENE 5: Closure & Next Steps
[Summary of learning objective]
[Connection to curriculum outcome]

[ACCESSIBILITY SECTION]
[ALT text for all visuals]
[Transcript for audio]
[Captions]

[CURRICULUM MAPPING]
Outcome Codes Addressed: [List]
Learning Difficulty Level: [Low/Medium/High]
Prior Knowledge Required: [List]

[HALLUCINATION AUDIT]
Fact-Checked: ✓ Yes
Sources Used: [List citations]
Misconceptions Addressed: [List]
Confidence Score: [%]
```

***

### **4. KEY FEATURES FOR YOUR PROTOTYPE**

**Feature 1: Pedagogical Template Engine**
- Pre-built templates for different teaching strategies
- "Worked Example → Faded Example → Independent Practice"
- "Contrast Examples" (what works vs. what doesn't)
- "Build & Refine" (simple version → complex version)

**Feature 2: Curriculum Alignment Dashboard**
- Real-time linking to CurricuLLM-AU API
- Show which curriculum outcomes the script addresses
- Highlight year-level appropriateness
- Flag if content exceeds/falls short of curriculum expectations

**Feature 3: Misconception Checker**
- Database of ~50-100 common misconceptions per subject (start with maths & science)
- Auto-detection: Does this script accidentally reinforce a misconception?
- Prompts teacher: "Include warning about common misconception: [X]?"

**Feature 4: Hallucination Safeguard Panel**
- Fact-check all factual claims against educational databases
- Flag unsourced statements
- Suggest citations for every factual claim
- Show confidence score (e.g., "98% verified")

**Feature 5: Cultural Safety Checker**
- Scan for stereotypes or culturally insensitive language
- Prompt for examples: "Use Australian Aboriginal perspectives in this history script?"
- Ensure diverse representation in characters/scenarios

**Feature 6: Accessibility Auto-Generation**
- Generate ALT text descriptions for all visual scenes
- Create captions from narration
- Include dyslexia-friendly formatting options

***

### **5. PROTOTYPE PROOF-OF-CONCEPT (What to Build)**

For a hackathon, focus on **one end-to-end flow** rather than all features:

#### **Minimum Viable Product (MVP):**

**Input:** Teacher describes topic + year level + learning objective

**Processing:**
1. Call CurricuLLM-AU API to get curriculum alignment
2. Use Claude/GPT to generate script with FAME framework (Fading, Alternating, Mistakes, Explanation)
3. Fact-check against Wikipedia API or curated curriculum database
4. Generate accessibility captions automatically

**Output:** Formatted script text ready for video AI tool

#### **Tech Stack Suggestion:**
- **Frontend**: React/Streamlit (simple, fast)
- **Backend**: Python (FastAPI or Flask)
- **APIs**: CurricuLLM-AU, OpenAI/Claude, Wikipedia/Wikidata
- **Database**: SQLite (misconceptions, curriculum facts)
- **Deployment**: Vercel/Streamlit Cloud (free, shareable)

***

### **6. YOUR 5-MINUTE VIDEO + PITCH DECK**

**Video Structure (2-3 min):**
- Problem: Show a poorly-written AI script (misconceptions, no pedagogy)
- Solution: Demonstrate your system generating a polished script
- Impact: Quick before/after comparison
- Call to Action: "Teachers get curriculum-aligned scripts in minutes"

**Pitch Deck Structure (5-7 slides):**

1. **Title Slide** — "ScriptSmith: AI Scripts Done Right"
2. **Problem** — Current AI videos lack pedagogy, contain misconceptions
3. **Solution Overview** — Three-layer architecture diagram
4. **How It Works** — User workflow visualization
5. **Evidence-Based Design** — Show the FAME framework + learning science
6. **Hallucination Prevention** — Show fact-checking flow
7. **Demo** — Screenshot of generated script vs. raw AI output
8. **Impact** — Teachers save time, students learn better
9. **Next Steps** — Roadmap (more subjects, multimodal, etc.)
10. **Call to Action** — "Join us in building better educational AI"

***

### **7. IMPLEMENTATION ROADMAP (for your hackathon submission)**

**What to have READY before submission:**

✅ **Working prototype** (Streamlit app or simple web interface)
- Input: Topic + Year Level
- Output: Formatted script with pedagogy embedded

✅ **Curriculum alignment demo** (even if just 5-10 outcomes from CurricuLLM-AU)

✅ **Misconception checker** (even if just hardcoded for 1-2 topics)

✅ **Fact-checking demo** (Wikipedia API check + confidence score)

✅ **Sample outputs** (3-4 example scripts showing before/after quality)

**Nice-to-Have:**
- Cultural safety checker
- Accessibility caption generation
- Fading progression visualization

***

### **8. COMPETITIVE ADVANTAGES**

Emphasize these in your pitch:

1. **Evidence-Based** — Every feature grounded in learning science (Sweller, Atkinson, cognitive load theory)
2. **Hallucination-Resistant** — RAG + fact-checking built in (not bolted on)
3. **Curriculum-Native** — Direct integration with CurricuLLM-AU (not generic)
4. **Teacher-Centered** — Designed for teachers, not tech enthusiasts
5. **Scalable** — Works across subjects, year levels, cultural contexts

***

### **10. SAMPLE SYSTEM PROMPT (to generate scripts)**

```
You are an expert educational script writer. Generate a script for:
Topic: [TOPIC]
Year Level: [YEAR]
Learning Objective: [OBJECTIVE]
Curriculum Code: [CODE]

Follow the FAME framework:
- Fading: Start with full worked example, gradually remove scaffolding
- Alternating: Alternate worked examples with student practice
- Mistakes: Include common errors (with corrections)
- Explanation: Include "think-aloud" narration explaining reasoning

Include:
1. Scene-by-scene breakdown with visual descriptions
2. Character/voice guidance
3. One "misconception warning" based on this list: [MISCONCEPTIONS]
4. Spaced retrieval question
5. Accessibility captions for each visual
6. Curriculum alignment markers

Avoid:
- Oversimplification that creates false mental models
- Culturally insensitive examples
- Unsourced factual claims
- Jargon not defined at this year level
```

***

This gives you a robust, well-researched foundation. The key differentiator is **embedding pedagogy + hallucination prevention from day one**, not treating them as afterthoughts.

## **System Design**
1. Use standard and reliable technologies for the backend and frontend.
2. Favour funcational approach over object-oriented approach.
3. Separate frontend and backend code.
4. Keep clear redable code. Create separate files along with proper folder structure.
5. Tech stack
| Layer           | Technology/Platform         | Hosting/Free Tier                          |
| --------------- | --------------------------- | ------------------------------------------ |
| Frontend        | ReactJS/NextJS               | Vercel (Free Tier)                            |
| Backend API     | FastAPI + Uvicorn           | Heroku (Free Tier)                         |
| Vector Store    | Pinecone / Weaviate / FAISS | Pinecone/Weaviate Free Tier or local FAISS |
| Language Model  | OpenAI GPT / Anthropic      | OpenAI free trial credits                  |
| Curriculum Data | CurricuLLM-AU API           | CurricuLLM-AU API                         |
| Database        | Supabase or MongoDB Atlas   | Supabase / MongoDB Free Tier               |
| Fact Source     | Wikipedia / Wikidata        | Free                                       |


[1](https://gist.github.com/VidhyaVarshanyJS/ee558d70f6278ee8a6c6e1375952e4ca)
[2](https://faculty.ai/insights/articles/key-takeaways-from-our-january-hackathon)
[3](https://assets.publishing.service.gov.uk/media/66cdb078f04c14b05511b322/Use_cases_for_generative_AI_in_education_user_research_report.pdf)
[4](https://www.gov.uk/government/publications/generative-ai-in-education-user-research-and-technical-report)
[5](https://www.ironhack.com/us/blog/ai-video-generator-tools-the-future-of-visual-storytelling-is-here)
[6](https://curricullm.com/developers)
[7](https://ora.ox.ac.uk/objects/uuid:c2ccd457-2953-4d38-bbc9-23f99267c7a6/files/mb6f3a869d19533fcb1ef3675ad0e45d3)
[8](https://projectpals.com/post/ai-fact-checking-101-teaching-students-to-verify-not-just-trust/)
[9](https://www.studocu.com/en-us/document/auburn-university/computer-science-and-software-engineering/hackathon-project-written-responses/119376390)
[10](https://curricullm.com)
[11](https://educationendowmentfoundation.org.uk/news/eef-blog-working-with-worked-examples-simple-techniques-to-enhance-their-effectiveness)
[12](https://verifywise.ai/lexicon/hallucination-detection)
[13](https://ec.europa.eu/programmes/erasmus-plus/project-result-content/bf7becf3-e203-4b43-8d35-3d678f6f495a/GamifyEU_publication_-_gamification_in_non-formal_education_and_youth_work.pdf)
[14](https://files.eric.ed.gov/fulltext/EJ1289131.pdf)
[15](https://evidenceforlearning.org.au/news/fame-tool-for-worked-examples)
[16](https://pmc.ncbi.nlm.nih.gov/articles/PMC10726751/)
[17](https://curricullm.com/terms)
[18](https://educationendowmentfoundation.org.uk/news/supporting-pupils-with-worked-examples)
[19](https://aws.amazon.com/blogs/aws/minimize-ai-hallucinations-and-deliver-up-to-99-verification-accuracy-with-automated-reasoning-checks-now-available/)
[20](https://www.linkedin.com/posts/teaching-how2s_ai-update-provides-extra-support-in-english-activity-7337848510232293376-wAWA)