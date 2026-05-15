# Human Review Prompt

Review the candidate ASR serving pipeline against the bundled automated scorecard. Focus only on facts visible in the repository and runtime output.

Answer:
1. Does the pipeline have clean ASRBackend boundaries?
2. Is CER calculation reproducible and normalization explicit?
3. Are preprocessing, inference, postprocessing, and evaluation separated?
4. Is the service production-oriented enough for latency, monitoring, errors, and deployment?
5. What are the top three changes needed before production use?

Return a concise verdict and do not change the numeric score unless the rubric explicitly requires manual adjustment.
