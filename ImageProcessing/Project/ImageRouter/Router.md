                   
             Image Quality
                   │
                   ▼
             512×512 image
                   │
                   ▼
        ┌─────────────────────┐
        │     MedSigLIP       │
        │                     │
        │ Vision Transformer  │
        │        +            │
        │ Text Transformer    │
        └──────────┬──────────┘
                   │
          image/text similarity
                   │
                   ▼
        ┌──────────────────────┐
        │ Candidate ranking    │
        └──────────┬───────────┘
                   │
      ┌────────────┼────────────┐
      ▼            ▼            ▼
    RASH         WOUND       SWELLING
