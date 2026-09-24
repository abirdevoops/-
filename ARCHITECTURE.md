# TruthLens AI Architecture

```text
                    ┌────────────────────────┐
                    │        USER            │
                    │ বাংলা / English        │
                    └───────────┬────────────┘
                                │
                    Registration / Login
                                │
                                ▼
                    ┌────────────────────────┐
                    │    Streamlit Web App   │
                    └───────────┬────────────┘
                                │
                         Image Upload
                                │
                    ┌───────────▼────────────┐
                    │     Pre-processing     │
                    │ RGB / validation       │
                    └───────────┬────────────┘
                                │
                 ┌──────────────┴──────────────┐
                 ▼                             ▼
       ┌──────────────────┐          ┌──────────────────┐
       │ Visual AI Model  │          │ Metadata / EXIF  │
       │ AI vs Natural    │          │ file information │
       └────────┬─────────┘          └────────┬─────────┘
                │                             │
                └──────────────┬──────────────┘
                               ▼
                    ┌────────────────────────┐
                    │ Evidence + Uncertainty │
                    │ Decision Layer          │
                    └───────────┬────────────┘
                                ▼
                ┌───────────────┼───────────────┐
                ▼               ▼               ▼
          Likely AI       Human Review      Likely Real
                │               │               │
                └───────────────┼───────────────┘
                                ▼
                     Explainable Result
                                │
                                ▼
                      Verify Before Share

              ┌─────────────────────────────────┐
              │ SQLite: users + scan summaries  │
              │ Admin-controlled dashboard      │
              └─────────────────────────────────┘
```
