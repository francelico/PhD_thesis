# Response to examiner comments

The comments below retain the original chapter and page references. Responses use the revised numbering: the new Background is Chapter 2, and the three research chapters are now Chapters 3–5.

## 1. Shared background

> The overall thesis is composed of three content chapters that represent the main technical contribution of the thesis. Each chapter represents a standalone scientific publication, hence contains its own related work section. However, considering that the thesis spans important topics at the intersection between many different disciplines in AI, it is useful to have a background chapter that provides: a) relevant benchmarks used in the literature and why certain benchmarks have been identified to be suitable for the work completed in this thesis; b) evaluation metrics, and c) definitions that are used across multiple chapters (e.g., Contextual MDP, sample efficiency, generalisation).

**Response.** Added Chapter 2 to introduce contextual MDPs, zero-shot generalisation, expected return, performance gaps and sample efficiency. Section 2.3 describes the benchmarks and their roles in the thesis. The research chapters refer back to these shared definitions, and the introduction’s outline and publication mapping include the new chapter.

## 2. The simulation bottleneck and the reality gap

> The same background chapter should be used to discuss the important “simulation bottleneck” problem and how it relates concretely to other important definitions in other fields, and how it’s different. Concretely, add a related-work subsection that cites the robotics lineage (Jakobi et al. 1995 on the reality gap; Tobin et al. 2017 and Zhao et al. 2020 on domain randomization and the sim2real survey) alongside the emerging agentic-RL lineage (e.g. the environment-quality/diversity distinction in recent LLM-agent environment surveys, and papers like RoboGen and CUA-Gym that try to automate away the engineering cost), and use that juxtaposition to justify why a general, domain-agnostic definition is needed rather than treating this as either "a robotics problem" or "an LLM-agent problem.”

**Response.** Section 2.2 defines the simulation bottleneck as repeated, domain-specific engineering and relates it to the reality gap. It connects the robotics literature of Jakobi et al., Tobin et al. and Zhao et al. with agentic-environment work, including RoboGen and CUA-Gym, to motivate a definition spanning physical and digital domains. Figure 2.1 illustrates the conceptual trends from handcrafted simulation to automated scenario generation and learned simulators.

## 3. Placement and notation of the results table

> Table 2.1 appears too early in the manuscript and some of the letters have not been defined before or are not described in the caption. Therefore, try to position it further down in your document to help the reader follow your narrative.

**Response.** Table 3.1 now follows the findings summary, after the architecture introduction and Figure 3.1. Its caption defines the symbols used in the table.

## 4. Placement of the notation paragraph

> I believe that the last paragraph of page 15 (“We briefly introduce…”) should be included in the next section considering that it’s introducing the main notation for that part of the work.

**Response.** Moved the paragraph beginning “We briefly introduce notation” to the start of Section 3.6, where the notation is used. The mutual-information estimator description remains in Section 3.5.

## 5. Definition of levels

> Section 2.5 refers to “levels” without defining what they are. This is important to understand how task definition relates to overall generalisation.

**Response.** Section 2.1 defines each environment instance through its fixed context and explains that Chapters 3 and 4 use “level” and “environment instance” interchangeably. Both chapters refer to the shared contextual framework.

## 6. Scope of the representation-learning study

> I think it’s important to clarify that Chapter 2, focuses on studying representation learning from the point of view of the learning objective rather than by analysis the representations induced by different neural architectures. For example, would a ViT encoder change your results? Would a pretrained visual encoder change your results? There are many interesting results in this direction: Williams, Emlyn, and Athanasios Polydoros. "Pretrained visual representations in reinforcement learning." Annual Conference Towards Autonomous Robotic Systems. Cham: Springer Nature Switzerland, 2024. Or Yuan, Zhecheng, et al. "Pre-trained image encoder for generalizable visual reinforcement learning." Advances in Neural Information Processing Systems 35 (2022): 13022-13037.

**Response.** Section 3.1 clarifies that the study concerns learning objectives and shared or separate actor–critic representations, using encoders trained from scratch. It does not draw conclusions about alternative architectures or pretrained encoders. The discussion cites relevant work on vision transformers and pretrained representations, including Yuan et al. and Williams and Polydoros.

## 7. ALE citation formatting

> Page 40 contains a reference to ALE Benchmark which is not formatted in the correct way (\citet{} vs \citep{})

**Response.** Changed the ALE benchmark citation to parenthetical form in the Procgen implementation descriptions in Chapters 3 and 4.

## 8. CleanRL spelling

> Page 41: ClearnRL -> CleanRL

**Response.** Corrected “ClearnRL” to “CleanRL” in the Brax implementation details.

## 9. Zero-shot generalisation and evaluation

> For Chapter 3 you again refer to zero-shot generalisation without defining what this is and how it is evaluated. Hence, the student should reuse the definitions in the new background section as justification for this part. The background potentially reusing material from Kirk, Robert, et al. "A survey of zero-shot generalisation in deep reinforcement learning." Journal of Artificial Intelligence Research 76 (2023): 201-264.

**Response.** Section 2.2 defines zero-shot generalisation as evaluation on unseen instances without further policy training, distinguishing held-out instances from distribution shifts. It introduces return-based evaluation and performance gaps, drawing on Kirk et al. Chapter 4 explicitly refers to this definition before developing its specialised generalisation analysis.

## 10. Practical assumptions of environment generation

> Chapter 3 should also clarify the relationship with the simulation bottleneck from the more practical point of view. This approach assumes that the agent can arbitrarily set up the configuration of the environment by sampling from a distribution of admissible ones. However, this is a benefit of having a simulator that might not translate to the real world. The student should reflect upon this in the limitations section.

**Response.** Chapter 4’s preamble and conclusion clarify that DRED requires a configurable simulator and a dataset of environment parameters representing the target distribution. The limitations state that DRED does not infer these parameters from observations alone, explaining the dependence on simulator capabilities.

## 11. Consistent thesis wording

> Page 64: “This paper presents”. Make sure that each chapter does not sound like a paper.

**Response.** Replaced paper-style self-references with chapter-specific wording, including “This chapter presents” in Chapter 4. The research-chapter preambles and the introduction identify the publications as adapted for the thesis.

## 12. Generator architecture and baseline comparisons

> Appendix 3.E.3: VAE architecture differences and GCN. Do all the other methods use the same visual encoder? How does your method compare with SOTA? Make sure to clarify this in the corresponding chapter.

**Response.** Appendix 4.E.3 describes the graph-based VAE encoder and decoder, distinguishes the generator from the agent’s visual encoder, and states that all methods use the same recurrent PPO architecture. It also explains the EL-DRED and VAE-DRED comparison and relates their performance to the reported UED baselines.

## 13. Consistent placement of related work

> In most chapters, you have related work after the technical content. Chapter 4 reports the related work first and then the technical content. Make sure that this is consistent in all the thesis chapters.

**Response.** All three research chapters now place Related Work immediately after Introduction and before Background or Preliminaries, in Sections 3.4, 4.4 and 5.4.

## 14. Training and test data in PERSIST

> Clarify the experimental setup of the Chapter 4 regarding the distribution of the data used for training vs test

**Response.** Chapter 5’s Dataset paragraph specifies the Free Play training policy and the use of held-out world-generation seeds for testing. Appendix 5.B describes the four human-study policies and the separate MineDojo baseline evaluation protocol.

## 15. PERSIST limitations and the simulation bottleneck

> Add a more detailed connection with the overall simulation bottleneck in Chapter 4 and how the limitations of PERSIST relate to this (particularly with regards to the fact that you need to have access to 3D representations that are only available in your simulated world). For instance, Appendix 4E should be promoted to the main text to allow a more detailed connection with the rest of the literature and to be explicit about limitations of the current work and how it can be extended in the future.

**Response.** Promoted the former limitations appendix to Section 5.9, before the conclusion. The discussion connects PERSIST’s dependence on 3D supervision to the simulation bottleneck and considers limitations and future extensions. Figures illustrating camera failures, world generation and long-rollout limitations accompany the relevant discussions.
