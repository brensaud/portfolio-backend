# AI Integration Master Plan

A complete map of every place AI can be used across the portfolio project
and the SaaS product — with implementation approach for each.

---

## AI capabilities used in this project

```
1. Text generation      → LLM (Groq, OpenAI, Anthropic)
2. Structured output    → LLM + Pydantic (no hallucinated schemas)
3. Embeddings           → OpenAI / Cohere → vector search (RAG)
4. Vision / OCR         → Claude Vision / GPT-4V / Tesseract
5. Classification       → LLM-based zero-shot classifier
6. Streaming            → Server-Sent Events → real-time UI
7. Function calling     → LLM decides which tool to invoke
8. Background AI jobs   → ARQ / Celery → async AI processing
9. Reranking            → Cohere Rerank → better RAG results
10. Guardrails          → input/output validation before/after LLM
```

---

## Provider strategy

```
Task                          Provider           Why
─────────────────────────────────────────────────────────────────
Fast structured output        Groq (Llama 3.3)   Fastest, cheapest, good accuracy
Complex reasoning             OpenAI GPT-4o      Best quality for hard tasks
Long context (>100k tokens)   Anthropic Claude   200k context window
Vision / image understanding  Claude Vision      Best OCR + image analysis
Embeddings                    OpenAI text-embedding-3-small  Cheap, accurate
Reranking                     Cohere Rerank      Best relevance scoring for RAG
Local / privacy-sensitive     Ollama (local)     For anything that shouldn't leave the machine
```

### Provider abstraction (already used in InterviewPilot AI)

```python
class LLMProvider(Protocol):
    async def complete(
        self,
        messages: list[Message],
        response_model: type[BaseModel] | None = None,
        stream: bool = False,
    ) -> BaseModel | str | AsyncGenerator: ...

class GroqProvider(LLMProvider): ...
class OpenAIProvider(LLMProvider): ...
class AnthropicProvider(LLMProvider): ...

# Config drives which provider is used:
# LLM_PROVIDER=groq | openai | anthropic | ollama
```

Swap providers with one env variable. No code changes needed.

---

## Zone 1 — Resume AI (highest value, most used)

### 1.1 Job description signal extractor
**Input:** raw JD text (any format)
**Output:** structured `JobSignals` Pydantic model

```python
class JobSignals(BaseModel):
    role_title: str
    company_name: str | None
    seniority_level: str          # "junior" | "mid" | "senior" | "staff" | "principal"
    required_skills: list[str]
    preferred_skills: list[str]
    responsibilities: list[str]
    culture_signals: list[str]    # "move fast", "high ownership", "production-first"
    red_flags: list[str]          # "unlimited PTO", "wear many hats"
    ats_keywords: list[str]       # terms that ATS systems scan for
    salary_range: str | None
    remote_policy: str | None
    company_size_hint: str | None
```

**Provider:** Groq (fast, structured output)
**When:** called automatically on every saved job

---

### 1.2 Resume tailoring engine
**Input:** `MasterResume` + `JobSignals`
**Output:** `TailoredResumeSuggestion` with diff per section

```python
class TailoredResumeSuggestion(BaseModel):
    headline: SuggestedChange
    summary_paragraphs: list[SuggestedChange]
    experience_bullets: dict[str, list[SuggestedChange]]  # keyed by experience ID
    skills_ordering: list[str]
    keywords_to_add: list[str]
    keywords_to_remove: list[str]
    reasoning: str  # why these changes were made

class SuggestedChange(BaseModel):
    original: str
    suggested: str
    confidence: float   # 0.0–1.0
    reason: str
```

**Provider:** GPT-4o (better reasoning for rewrites)
**Fallback:** Groq (faster, cheaper, slightly lower quality)
**When:** user clicks "Tailor with AI" on a job

---

### 1.3 ATS keyword scorer
**Input:** resume text + job description
**Output:** `ATSScore` with breakdown

```python
class ATSScore(BaseModel):
    overall_score: int            # 0–100
    keyword_coverage: float       # 0.0–1.0
    missing_required: list[str]
    missing_preferred: list[str]
    present_keywords: list[str]
    skills_gap: list[str]
    strengths: list[str]
    weaknesses: list[str]
    suggestions: list[ActionableSuggestion]
    bullet_feedback: list[BulletFeedback]

class ActionableSuggestion(BaseModel):
    suggestion: str
    impact: str   # "high" | "medium" | "low"
    effort: str   # "quick fix" | "minor edit" | "significant rewrite"
```

**Provider:** Groq (keyword matching + semantic analysis)
**Enhancement:** regex-based exact keyword check FIRST, then LLM for semantic gaps

---

### 1.4 Bullet point strength analyser
**Input:** list of resume bullet strings
**Output:** per-bullet score + rewrite suggestion

```python
class BulletAnalysis(BaseModel):
    original: str
    score: int              # 0–100
    action_verb: str        # the detected verb
    verb_strength: str      # "strong" | "weak" | "missing"
    is_quantified: bool
    is_specific: bool
    is_concise: bool
    weak_phrases: list[str] # phrases flagged
    suggested_rewrite: str
    improvement_tips: list[str]
```

**Provider:** Groq (fast, runs per bullet)
**Pattern:** regex for weak verb detection FIRST (cheap), LLM only for rewrites

---

### 1.5 Cover letter generator
**Input:** resume version + JD + company context + tone preference
**Output:** `CoverLetter` with 3 structured paragraphs

```python
class CoverLetter(BaseModel):
    opening: str        # why this role, why this company (specific)
    body: str           # most relevant experience + project
    closing: str        # enthusiasm + call to action
    subject_line: str   # email subject suggestion
    word_count: int
```

**Provider:** GPT-4o (tone + personalisation quality)
**Streaming:** yes — user sees it generate in real-time

---

### 1.6 Skills gap analysis
**Input:** master resume skills + list of target JDs
**Output:** `SkillsGapReport`

```python
class SkillsGapReport(BaseModel):
    skills_you_have: list[str]
    skills_to_learn: list[PrioritisedSkill]
    quick_wins: list[str]       # ≤ 1 week to add
    big_bets: list[str]         # months of learning
    summary_narrative: str

class PrioritisedSkill(BaseModel):
    name: str
    frequency_in_jds: int       # how many target JDs mention it
    importance: str             # "required" | "preferred"
    estimated_weeks: int        # rough learning time estimate
    learning_path: str          # "1 tutorial + 1 project"
```

**Provider:** Groq
**When:** user pastes multiple JDs in the skills gap tab

---

### 1.7 Interview question generator
**Input:** resume version + JD + interview type
**Output:** `InterviewPrepSet`

```python
class InterviewQuestion(BaseModel):
    question: str
    category: str           # "technical" | "behavioural" | "system_design"
    why_likely: str         # why an interviewer at this company would ask this
    answer_direction: str   # suggested approach (not the full answer)
    relevant_experience: str | None  # which of your projects to draw from

class InterviewPrepSet(BaseModel):
    technical: list[InterviewQuestion]
    behavioural: list[InterviewQuestion]
    system_design: list[InterviewQuestion]
    project_deep_dives: list[InterviewQuestion]
```

**Provider:** GPT-4o (requires reasoning about company context)
**When:** 24 hours before a scheduled interview

---

## Zone 2 — Job Management AI

### 2.1 Job description parser (all three input methods)
**Input:** URL / image / pasted text
**Output:** `ParsedJobPosting`

```python
class ParsedJobPosting(BaseModel):
    title: str
    company: str | None
    location: str | None
    remote_policy: str | None
    salary_range: str | None
    job_description: str        # cleaned full text
    apply_url: str | None
    deadline: date | None
    source_type: str            # "url" | "image" | "text"
    extraction_confidence: float # 0.0–1.0
```

**For URL:** fetch HTML + BeautifulSoup + LLM to extract clean structure
**For image/screenshot:** Claude Vision (best OCR + layout understanding)
**For pasted text:** Groq (fast cleaning + structuring)

---

### 2.2 Job fit scorer
**Input:** user's master resume + job posting
**Output:** `JobFitScore`

```python
class JobFitScore(BaseModel):
    overall: int                # 0–100
    skills_match: float
    seniority_match: float
    culture_fit: float          # based on past application history
    role_type_match: float      # backend vs frontend vs fullstack
    recommendation: str         # "Strong match", "Apply with tailored resume", "Skills gap too large"
    key_reasons: list[str]
```

**When:** automatically when a job is saved
**Shown on:** job card in the Job Board

---

### 2.3 Contact message classifier
**Input:** contact message (name, email, subject, body)
**Output:** `MessageClassification`

```python
class MessageClassification(BaseModel):
    type: str           # "hiring_inquiry" | "collaboration" | "question" | "feedback" | "spam"
    priority: str       # "high" | "normal" | "low"
    is_recruiter: bool
    recruiter_company: str | None
    key_topics: list[str]
    sentiment: str      # "positive" | "neutral" | "negative"
    requires_reply: bool
    draft_opener: str   # first sentence of a suggested reply
```

**Provider:** Groq (runs on every new message as background job)
**Pattern:** rule-based first (recruiter domain detection), LLM for nuanced classification

---

### 2.4 Rejection analyser
**Input:** application data (stage reached, JD, resume version used, interview notes)
**Output:** `RejectionAnalysis`

```python
class RejectionAnalysis(BaseModel):
    likely_reason: str
    confidence: str         # "high" | "medium" | "low"
    stage_analysis: str     # what the rejection stage suggests
    resume_role: str        # was the resume likely the issue?
    prep_role: str          # was preparation likely the issue?
    actionable_next_steps: list[str]
    avoid_in_future: list[str]
```

---

### 2.5 Offer evaluation advisor
**Input:** offer details + salary intelligence + your priorities
**Output:** `OfferEvaluation`

```python
class OfferEvaluation(BaseModel):
    overall_verdict: str        # "Strong", "Fair", "Below market", "Exceptional"
    total_comp_estimate: int    # annualised
    market_comparison: str      # vs P50, P75
    negotiation_potential: str  # "high room", "some room", "likely final"
    counter_offer_suggestion: CounterOffer | None
    red_flags: list[str]        # vague equity, no vesting cliff, etc.
    green_flags: list[str]
    negotiation_script: str     # what to say

class CounterOffer(BaseModel):
    base_ask: int
    equity_ask: str | None
    other_asks: list[str]
    reasoning: str
```

---

### 2.6 Cold outreach email writer
**Input:** target person, company, context, resume version
**Output:** personalised cold email under 100 words

```python
class ColdEmail(BaseModel):
    subject: str
    body: str
    word_count: int
    personalization_signals: list[str]  # what specific details were used
    tone: str
```

**Constraint:** prompt instructs the LLM to:
- Reference ONE specific technical decision / blog post / project from the company
- Keep under 100 words
- No "I noticed you're hiring" phrases
- End with a soft ask, not a hard pitch

---

## Zone 3 — Content AI

### 3.1 Article idea generator
**Input:** your published articles, projects, skills, top LinkedIn posts
**Output:** `ArticleIdeaList`

```python
class ArticleIdea(BaseModel):
    title: str
    angle: str              # the specific take / argument
    target_audience: str
    difficulty_to_write: str    # "quick" | "medium" | "deep"
    estimated_search_volume: str  # "niche" | "moderate" | "high"
    relevance_to_your_work: str   # why you're qualified to write this
    outline: list[str]      # 5–7 section headings

class ArticleIdeaList(BaseModel):
    ideas: list[ArticleIdea]
    rationale: str
```

**When:** user opens "Get article ideas" in the admin

---

### 3.2 Article writing assistant (inline suggestions)
- While writing in the Markdown editor: highlight text → "Improve this"
- Options: make clearer / make more concise / add example / fix tone
- Streaming response inserted inline
- "Continue writing" — generates the next paragraph from context

**Implementation:** SSE (Server-Sent Events) for real-time streaming in the editor

---

### 3.3 Article SEO optimiser
**Input:** article title + body
**Output:** `ArticleSEO`

```python
class ArticleSEO(BaseModel):
    suggested_title: str            # SEO-optimised version
    meta_description: str           # 155 chars max
    focus_keyword: str
    secondary_keywords: list[str]
    readability_score: float        # Flesch-Kincaid
    heading_structure_score: float  # proper H2/H3 hierarchy
    internal_link_suggestions: list[str]  # link to your other content
    missing_elements: list[str]     # "no conclusion", "no code example"
```

---

### 3.4 Case study generator
**Input:** project data (tech stack, description, challenges) + optional raw notes
**Output:** structured case study sections with suggested content

**Sections AI drafts:**
- Problem statement: "What problem were you solving?"
- Architecture overview: extract from tech stack + description
- Key technical decisions: "What alternatives did you consider?"
- Implementation highlights: code-level specifics to discuss
- Lessons learned: common patterns from similar projects

Admin reviews + edits each section. AI provides the skeleton.

---

### 3.5 Project description improver
**Input:** current project description
**Output:** improved version with specific options

```python
class ImprovedDescription(BaseModel):
    concise_version: str        # 1-sentence (for cards)
    standard_version: str       # 2-3 sentences (for project page)
    technical_version: str      # focus on architecture decisions
    recruiter_version: str      # focus on impact and outcomes
```

---

## Zone 4 — Portfolio AI

### 4.1 Bio / headline optimiser
**Input:** current headline + bio + target roles
**Output:** multiple variants with different angles

```python
class BioVariants(BaseModel):
    technical_focus: str        # "I build..."
    outcome_focus: str          # "I help companies..."
    personality_focus: str      # "Python engineer who..."
    recruiter_facing: str       # ATS-optimised professional summary
    reasoning: str              # which to use when
```

---

### 4.2 Portfolio gap analysis
**Input:** your projects, articles, skills, target roles
**Output:** what's missing from your portfolio to land those roles

```python
class PortfolioGap(BaseModel):
    missing_project_types: list[str]  # "you have no system design projects"
    missing_content: list[str]        # "no articles on databases"
    weak_sections: list[str]
    strengths: list[str]
    priority_improvements: list[str]
    estimated_impact: str
```

---

### 4.3 "Ask me anything" — RAG chat widget (public-facing)

Visitors can ask questions about your experience and projects.
AI answers using your portfolio content as context.

**Architecture:**

```
User types question
        ↓
Embed the question (OpenAI text-embedding-3-small)
        ↓
Vector search on pgvector index
  - Articles (chunked into paragraphs)
  - Projects (description + tech stack)
  - Resume entries (experience bullets)
  - Case studies
        ↓
Top 5 most relevant chunks retrieved
        ↓
Reranker (Cohere Rerank) picks top 3
        ↓
LLM prompt:
  "You are {name}'s portfolio assistant.
   Answer only from the provided context.
   If unsure, say so. Do not invent experience."
        ↓
Streaming answer shown to visitor
  + Source citation: "Based on your Projects section"
```

**Rate limiting:** 5 questions per IP per hour
**Guardrail:** output checked for hallucination (answer must reference context)
**Provider:** GPT-4o-mini (cheap, good enough for Q&A)

---

### 4.4 Availability signal detector
**Input:** recent LinkedIn posts + job search history + calendar
**Output:** suggested availability status update

"You've had 3 interviews this week — should your availability status still say 'Open'?"

---

## Zone 5 — Analytics AI

### 5.1 Traffic insights narrator
**Input:** analytics data (last 7/30/90 days)
**Output:** plain-English narrative summary

```
"Your portfolio traffic increased 34% this week. The spike on Tuesday
 was driven by your LinkedIn post about JWT auth — 67 visitors from LinkedIn.
 Your 'InterviewPilot AI' project page is your most visited — 
 consider adding a case study to convert those views."
```

**Provider:** Groq (cheap, runs weekly)
**When:** Monday morning — shown on admin dashboard

---

### 5.2 Content performance predictor
**Input:** draft article title + intro paragraph
**Output:** predicted performance before publishing

```python
class ContentPrediction(BaseModel):
    estimated_views_30d: str    # "50–200" | "200–1000" | "1000+"
    engagement_prediction: str  # "low" | "medium" | "high"
    viral_potential: str
    audience_match: str
    improvement_suggestions: list[str]
    best_publish_day: str       # "Tuesday or Wednesday"
    best_publish_time: str      # "9am–11am your timezone"
```

---

### 5.3 Recruiter intent analyser
**Input:** contact message + visitor analytics (referrer, pages visited)
**Output:** recruiter intent score + context

"This person visited your resume page + InterviewPilot project + contact page
 in one session. High hiring intent signal."

---

## Zone 6 — LinkedIn AI

### 6.1 LinkedIn post performance analyser
**Input:** your top-performing posts (from export)
**Output:** what patterns make your posts perform well

```python
class PostPatterns(BaseModel):
    common_topics: list[str]
    common_formats: list[str]   # "listicle", "story", "opinion", "technical"
    best_performing_hooks: list[str]
    optimal_length: str
    posting_time_insights: str
    audience_engagement_triggers: list[str]
```

---

### 6.2 LinkedIn post writer
**Input:** topic + angle + your voice patterns
**Output:** LinkedIn post draft in your style

**Voice learning:** fine-tune on your past posts to match your writing style.

---

### 6.3 Profile headline A/B tester
**Input:** 3 headline variants
**Output:** predicted click-through rate + recommendation

Based on analysis of what headlines work for engineers at your target companies.

---

## Zone 7 — Administrative AI

### 7.1 Contact message smart reply
**Input:** contact message + your resume + availability status
**Output:** draft reply personalised to the message type

```
Message type: hiring inquiry from Goldman Sachs
Draft reply:
  "Hi Sarah, thanks for reaching out about the backend engineering
   role. I'm currently open to new opportunities and would be 
   interested in learning more. My background is in Python/FastAPI
   systems — I've recently completed an admin panel for my portfolio
   that demonstrates my approach to authentication and audit logging.
   Happy to connect for a call. When works for you?"
```

---

### 7.2 Audit log anomaly detector
**Input:** admin_audit_logs over past 24 hours
**Output:** alert if unusual pattern detected

"20 login attempts from 3 different IPs in the last hour — possible
 brute force attack. Current rate limiting is blocking them."

---

## Zone 8 — AI Infrastructure (the plumbing)

### 8.1 Provider abstraction layer

```python
# app/services/ai/providers/base.py
class AIProvider(Protocol):
    async def complete(
        self,
        messages: list[ChatMessage],
        response_model: type[T] | None = None,
        stream: bool = False,
        temperature: float = 0.3,
        max_tokens: int | None = None,
    ) -> T | str | AsyncGenerator[str, None]: ...

    async def embed(self, text: str) -> list[float]: ...
```

### 8.2 Prompt template registry

```python
# app/services/ai/prompts.py
# All prompts stored as versioned templates
PROMPTS = {
    "resume.tailor.v2": PromptTemplate(
        system="You are an expert resume writer...",
        user_template="Job signals: {signals}\nMaster resume: {resume}",
        version="2.0",
        last_updated="2026-07-07",
    ),
    "contact.classify.v1": PromptTemplate(...),
    "article.seo.v1": PromptTemplate(...),
}
```

Prompts are versioned and tracked. A/B test different prompt versions.

### 8.3 Structured output with validation

```python
# All LLM responses go through Pydantic validation
# If validation fails → retry with corrected prompt
async def structured_complete(
    messages: list[ChatMessage],
    response_model: type[T],
    max_retries: int = 3,
) -> T:
    for attempt in range(max_retries):
        raw = await provider.complete(messages)
        try:
            return response_model.model_validate_json(raw)
        except ValidationError as e:
            # Add error feedback to messages and retry
            messages.append({"role": "user", "content": f"Fix: {e}"})
    raise AIStructuredOutputError("Max retries exceeded")
```

### 8.4 AI result caching

```python
# Cache AI results to avoid redundant calls
# Cache key: hash(prompt + input)
# TTL: configurable per feature

@cached(ttl=3600, key_fn=lambda jd: f"jd_signals:{sha256(jd)}")
async def extract_jd_signals(jd_text: str) -> JobSignals: ...
```

Same JD analysed twice → served from cache. Significant cost reduction.

### 8.5 Background AI queue

```python
# All AI operations triggered asynchronously
# User gets result via webhook or polling

# On contact message received:
await ai_queue.enqueue(
    "classify_contact_message",
    message_id=str(message.id),
    priority="high",
)

# On job saved:
await ai_queue.enqueue(
    "extract_jd_signals",
    job_id=str(job.id),
    priority="normal",
)
```

Non-blocking. User experience is never delayed by AI processing.

### 8.6 AI cost tracker

```python
# Every AI call logged
ai_usage_logs
  id              UUID
  user_id         UUID
  feature         VARCHAR    # "resume.tailor", "contact.classify"
  provider        VARCHAR    # "groq", "openai"
  model           VARCHAR    # "llama-3.3-70b", "gpt-4o"
  input_tokens    INTEGER
  output_tokens   INTEGER
  cost_usd        DECIMAL(10,6)
  duration_ms     INTEGER
  created_at      TIMESTAMPTZ
```

Admin sees: AI spend this month, cost per feature, per-user cost.

### 8.7 Guardrails

```python
# Input guardrails — before sending to LLM
class InputGuardrail:
    def check(self, text: str) -> GuardrailResult:
        # 1. Max length check (prevent prompt injection via huge inputs)
        # 2. Injection pattern detection (ignore previous instructions...)
        # 3. PII detection (don't send SSN/DOB to external LLMs)
        # 4. Profanity/abuse filter

# Output guardrails — after LLM response
class OutputGuardrail:
    def check(self, response: str, context: str) -> GuardrailResult:
        # 1. Hallucination check (RAG answers must reference context)
        # 2. Length bounds (no 50-word "summaries")
        # 3. Sensitive data in output check
```

### 8.8 Streaming implementation

```python
# FastAPI SSE endpoint for streaming AI responses
@router.post("/admin/api/resume/ai/tailor/stream")
async def stream_resume_tailor(
    request: TailorRequest,
    admin: str = Depends(get_current_admin),
) -> EventSourceResponse:
    async def generate():
        async for chunk in ai_service.stream_tailor(request):
            yield ServerSentEvent(data=chunk.model_dump_json())
        yield ServerSentEvent(data="[DONE]")
    return EventSourceResponse(generate())
```

```typescript
// Frontend consumes the stream
const source = new EventSource('/admin/api/resume/ai/tailor/stream')
source.onmessage = (event) => {
  if (event.data === '[DONE]') { source.close(); return }
  const chunk = JSON.parse(event.data)
  setGeneratedContent(prev => prev + chunk.text)
}
```

---

## Complete AI feature map

| Feature | Zone | Provider | Async? | Streaming? | Priority |
|---|---|---|---|---|---|
| JD signal extractor | Resume | Groq | Yes | No | ⭐⭐⭐ |
| Resume tailoring | Resume | GPT-4o | No | Yes | ⭐⭐⭐ |
| ATS score analyser | Resume | Groq | No | No | ⭐⭐⭐ |
| Bullet point scorer | Resume | Groq | No | No | ⭐⭐⭐ |
| Cover letter generator | Resume | GPT-4o | No | Yes | ⭐⭐⭐ |
| Skills gap analysis | Resume | Groq | No | No | ⭐⭐ |
| Interview prep generator | Resume | GPT-4o | No | No | ⭐⭐ |
| Offer evaluation advisor | Jobs | GPT-4o | No | No | ⭐⭐ |
| JD parser (URL/image/text) | Jobs | Claude Vision | Yes | No | ⭐⭐⭐ |
| Job fit scorer | Jobs | Groq | Yes | No | ⭐⭐⭐ |
| Contact classifier | Jobs | Groq | Yes | No | ⭐⭐⭐ |
| Rejection analyser | Jobs | GPT-4o | No | No | ⭐⭐ |
| Cold outreach writer | Jobs | GPT-4o | No | Yes | ⭐⭐ |
| Ask me anything (RAG) | Portfolio | GPT-4o-mini | No | Yes | ⭐⭐⭐ |
| Bio/headline optimiser | Portfolio | Groq | No | No | ⭐⭐ |
| Portfolio gap analysis | Portfolio | GPT-4o | No | No | ⭐⭐ |
| Article idea generator | Content | GPT-4o | No | No | ⭐⭐ |
| Article writing assistant | Content | GPT-4o | No | Yes | ⭐⭐ |
| Article SEO optimiser | Content | Groq | No | No | ⭐⭐ |
| Case study drafter | Content | GPT-4o | No | Yes | ⭐ |
| Project description improver | Content | Groq | No | No | ⭐⭐ |
| Traffic insights narrator | Analytics | Groq | Yes | No | ⭐ |
| LinkedIn post analyser | LinkedIn | Groq | No | No | ⭐ |
| Smart reply for contact msg | Admin | GPT-4o | No | Yes | ⭐⭐ |
| Audit log anomaly detector | Admin | Groq | Yes | No | ⭐ |

---

## AI implementation order

```
Sprint B  Resume tailoring + ATS scorer (highest ROI, core feature)
Sprint C  JD parser (URL/image/text) — all three input methods
Sprint D  Contact classifier (runs on every new message)
Sprint E  Cover letter generator
Sprint F  Job fit scorer (auto-runs on job save)
Sprint G  Ask me anything / RAG chat widget
Sprint H  Interview prep generator
Sprint I  Skills gap analysis
Sprint J  Rejection analyser + offer evaluator
Sprint K  Article AI tools (idea gen, writing assistant, SEO)
Sprint L  LinkedIn post analyser + cold outreach writer
Sprint M  Analytics narrator + portfolio gap analysis
```

---

## Cost estimates (per feature, per use)

| Feature | Provider | Input tokens | Output tokens | Cost/use |
|---|---|---|---|---|
| JD signal extraction | Groq | ~1,000 | ~300 | $0.001 |
| Resume tailoring | GPT-4o | ~3,000 | ~1,500 | $0.065 |
| ATS score analysis | Groq | ~2,000 | ~500 | $0.003 |
| Cover letter | GPT-4o | ~2,000 | ~400 | $0.033 |
| Contact classification | Groq | ~300 | ~150 | $0.0005 |
| RAG answer | GPT-4o-mini | ~2,000 | ~300 | $0.003 |
| Interview prep | GPT-4o | ~3,000 | ~2,000 | $0.085 |

At Pro plan pricing ($19/mo):
- 50 resume tailors/month = $3.25 AI cost → very profitable
- 200 RAG questions/month = $0.60 AI cost → negligible
- 20 cover letters/month = $0.66 AI cost → very profitable

**Total AI cost for a heavy Pro user: ~$5–8/month**
**Revenue from that user: $19/month**
**Margin: 58–74% after AI costs alone**
