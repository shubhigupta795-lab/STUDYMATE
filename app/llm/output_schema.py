from pydantic import BaseModel, Field


class EvidenceItem(BaseModel):
    item: str = Field(description="The extracted fact, claim, finding, or observation.")
    source_location: str = Field(
        description="Where this appears in the source, such as page 7, section 3, heading, or transcript timestamp. Use 'Not specified' when unavailable."
    )


class MethodologyItem(BaseModel):
    item: str = Field(description="Important methodology, approach, experiment, or design choice.")
    source_location: str = Field(description="Source location or 'Not specified'.")


class RecentAdvancement(BaseModel):
    advancement: str = Field(description="A relevant development since the source was published, grounded in current web information.")
    why_it_matters: str = Field(description="How this changes, strengthens, weakens, or contextualizes the older research.")
    approximate_date: str = Field(description="Publication/release year or period for the advancement.")
    sources: list[str] = Field(default_factory=list, description="URLs or source names supporting the advancement when available.")


class ResearchExtraction(BaseModel):
    title: str = Field(description="Title of the source or the best inferred title.")
    summary: str = Field(description="A concise but information-dense summary of the source.")
    research_problem: str = Field(description="The problem/question the research addresses.")
    research_objective: str = Field(description="What the authors set out to achieve or establish.")
    novelty: str = Field(description="What is new or claimed to be new in the source.")
    key_concepts: list[EvidenceItem] = Field(default_factory=list)
    methodology: list[MethodologyItem] = Field(default_factory=list)
    findings: list[EvidenceItem] = Field(default_factory=list)
    important_facts: list[EvidenceItem] = Field(default_factory=list)
    claims: list[EvidenceItem] = Field(default_factory=list)
    limitations: list[EvidenceItem] = Field(default_factory=list)
    what_they_could_not_establish: list[EvidenceItem] = Field(default_factory=list)
    what_can_be_done_better: list[EvidenceItem] = Field(default_factory=list)
    potentially_overlooked: list[EvidenceItem] = Field(default_factory=list)
    practical_implications: list[EvidenceItem] = Field(default_factory=list)
    open_research_questions: list[str] = Field(default_factory=list)
    fresh_knowledge: list[RecentAdvancement] = Field(default_factory=list)
    important_references: list[str] = Field(default_factory=list)
