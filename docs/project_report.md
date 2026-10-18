# Project Report: Language Identification System Using Natural Language Processing

## 1. Abstract

This project implements a Language Identification System that accepts text from a user and predicts the language in which it is written. The system uses a pretrained language-identification model provided by `py3langid`, wrapped in a Python module that validates input, evaluates detection results, and returns structured outputs.

The application provides a Streamlit web interface and a FastAPI REST API. It is designed to identify English, Kannada, Hindi, and other supported languages. It supports Unicode text, including Kannada and Devanagari scripts, and provides warnings for short, ambiguous, or mixed-script input.

Automated tests are implemented using `pytest`. The development report records a test run of 62 passed tests and one warning in a Python 3.12.3 environment. This result must be distinguished from any subsequent test run on another Python version. The project demonstrates the practical application of natural language processing for multilingual text identification.

## 2. Introduction

Language identification (LID) is the task of determining the natural language in which a piece of text is written. It is commonly used as an initial step in text-processing applications such as machine translation, search indexing, multilingual information retrieval, spell checking, and content moderation.

Language identification is particularly useful in multilingual environments such as India, where people communicate in English, Kannada, Hindi, and many other languages. These languages use different writing systems, and some languages share scripts, making automatic identification a challenging problem.

This project develops a software application that accepts user-provided text, identifies its most likely language, and communicates uncertainty when the input does not provide enough reliable linguistic information.

## 3. Problem Statement

Given a piece of text, the system must identify its most likely language and return a structured result containing the language name, language code, and available model scores.

The system must validate input and handle empty, invalid, extremely short, ambiguous, or non-linguistic text appropriately. It should avoid presenting uncertain predictions as guaranteed results.

## 4. Objectives

The main objectives are:

1. To identify English, Kannada, Hindi, and other languages supported by the selected model.
2. To integrate a pretrained language-identification model without training a new model from scratch.
3. To provide an accessible web interface for entering text and viewing predictions.
4. To expose language-identification functionality through a REST API.
5. To handle Unicode text, invalid input, ambiguous text, and mixed-script input appropriately.
6. To implement automated tests for normal and edge cases.
7. To provide documentation and package the application for reproducibility and GitHub publication.

## 5. Scope of the Project

### 5.1 In scope

- Language identification from user-provided Unicode text.
- Identification of English, Kannada, Hindi, and other languages supported by the selected model.
- A Streamlit-based web interface.
- A FastAPI REST API.
- Input validation and reliability warnings.
- Display of language names, language codes, and model scores where available.
- Session-based detection history, if enabled in the implementation.
- Automated testing and project documentation.

### 5.2 Out of scope

- Speech recognition and audio-based language identification.
- Language identification from images or scanned documents.
- Sentence-level segmentation of multilingual text.
- Reliable identification of romanized or transliterated languages.
- Training or fine-tuning a new language-identification model.
- Benchmark-based accuracy evaluation on a large, independently labelled dataset.
- Guaranteed identification of extremely short or ambiguous text.

## 6. Background on Language Identification

Language identification can be approached using statistical, probabilistic, and neural methods.

Character n-gram methods represent text using sequences of characters and compare them with language-specific patterns. Cavnar and Trenkle (1994) describe an early n-gram-based approach to text categorization.

Probabilistic approaches estimate the likelihood of a language given observed character or byte sequences. Lui and Baldwin (2012) introduced `langid.py`, an off-the-shelf language-identification tool designed for practical use.

Jauhiainen et al. (2019) provide a survey of automatic language-identification methods, applications, and challenges.

Language identification becomes more difficult when the text is short, contains only common words, includes multiple languages, or belongs to closely related languages. Script information can provide useful evidence. For example, Kannada commonly uses the Kannada script, while Hindi commonly uses Devanagari. However, languages such as Hindi and Marathi share Devanagari, so script alone cannot reliably distinguish them.

### 6.1 Library selection

Lingua was considered as a candidate language-identification library. During development, its installed version was inspected and found not to provide the required Kannada support. The project therefore selected `py3langid`, whose model was reported to support Kannada and several other Indian languages.

The model is integrated through a Python module so that the user interface and API can share the same detection logic.

The installed library version and supported language list should be checked against the project's actual environment before submission.

## 7. System Requirements

### 7.1 Hardware requirements

- A computer capable of running Python and a modern web browser.
- Sufficient memory to run the application and its dependencies.
- No dedicated GPU is required for the described pretrained-model approach.

A minimum memory requirement has not been established through formal measurement.

### 7.2 Software requirements

- Python compatible with the selected dependency versions.
- pip for dependency installation.
- Streamlit for the web interface.
- FastAPI and Uvicorn for the REST API, if included.
- `py3langid` for language identification.
- pytest for automated testing.
- HTTPX for API testing, if used by the test suite.
- Visual Studio Code or another Python-compatible editor.
- Git for version control and GitHub publication.

The exact Python version and dependency versions should be recorded from the environment used for final testing.

## 8. Methodology

The project was developed using the following workflow:

1. Identify the functional requirements, including mandatory support for English, Kannada, and Hindi.
2. Evaluate available pretrained language-identification libraries against the required language coverage.
3. Select a suitable library and integrate it into a dedicated Python detection module.
4. Implement input validation, Unicode handling, result formatting, and uncertainty warnings.
5. Build a Streamlit interface for interactive language identification.
6. Implement REST endpoints using FastAPI, where included.
7. Develop automated tests for common inputs, supported languages, and edge cases.
8. Execute the test suite and address failures.
9. Document the architecture, implementation, limitations, and test results.
10. Prepare the project for GitHub publication and academic submission.

## 9. System Architecture

The application separates the user interface, API, and language-identification logic.

The Streamlit interface accepts text and displays results. The FastAPI application exposes language-identification functionality through HTTP endpoints. Both components use the shared detection module, which calls the pretrained `py3langid` model.

Refer to `architecture.md` for the detailed architecture, provided that this file exists in the project's documentation directory.

### 9.1 Architecture workflow

1. The user enters text through the web interface or submits a request to the API.
2. The input is validated and normalized.
3. The detection module checks whether the text contains sufficient linguistic content.
4. The pretrained model ranks supported language candidates.
5. The detection module applies the project's reliability rules.
6. A structured result is returned to the interface or API client.
7. The result and any relevant warnings are displayed to the user.

## 10. Module Descriptions

| Module | Responsibility |
|---|---|
| `detector.py` | Provides the language-detection logic, result structure, language-name mapping, and reliability checks. |
| `app.py` | Implements the Streamlit user interface, example inputs, detection controls, and session history. |
| `api.py` | Implements REST endpoints and request/response validation through FastAPI. |
| `config.py` | Stores configurable thresholds and input limits. |
| `utils.py` | Contains reusable input-processing and helper functions. |
| `scripts/detect_cli.py` | Provides command-line access to the detector, if included. |
| `tests/` | Contains automated tests for language identification and edge cases. |
| `docs/` | Contains the project report, architecture documentation, and testing information. |

The module descriptions above should be adjusted if the final project structure differs from this list.

## 11. Detection Workflow

The intended detection workflow is as follows:

1. Validate the input type.
2. Reject empty or whitespace-only text.
3. Enforce the configured maximum input length.
4. Normalize Unicode text and whitespace where appropriate.
5. Count alphabetic characters and check whether sufficient linguistic content is present.
6. Return an inconclusive result when the text contains too little linguistic information.
7. Obtain language candidates and scores from the pretrained model.
8. Apply the project's configured reliability threshold.
9. Return the detected language, language code, score, alternatives, and relevant warnings.
10. Display the result through the web interface or return it through the API.

The implementation described in the development notes uses a minimum of two letters, a warning threshold of fewer than fifteen letters, and a model-score threshold of 0.30. These are configurable engineering choices rather than experimentally established optimal values.

The exact behavior should be confirmed against `config.py` and `detector.py` before submission.

## 12. Implementation Details

### 12.1 Pretrained model

The application uses `py3langid` for language identification. The library is integrated into the detection module, avoiding the need to train a model from scratch.

### 12.2 Input validation

Input validation prevents empty text, invalid input types, and excessively long strings from being processed as normal language samples. Very short or non-linguistic inputs are handled through the project's configured reliability checks.

### 12.3 Scores and confidence

The implementation uses normalized model scores when configured through the library. These scores indicate the model's relative support for candidate languages and must not be interpreted as calibrated probabilities of correctness.

A high score does not guarantee that the predicted language is correct, especially for short or mixed-language input.

### 12.4 Language names and codes

The application maps language identifiers to readable language names. The language codes returned by the model should be documented according to the code system used by the library. The exact mapping should be checked against the implementation.

### 12.5 Unicode and script handling

The application is designed to process Unicode text, including Kannada and Devanagari characters. Script information can provide useful warnings when multiple writing systems occur in one input.

However, mixed-script detection does not necessarily identify every mixed-language sentence. English and Kannada, for example, can appear together in one text, and a language classifier may still assign the entire input to one language.

### 12.6 User interface

The Streamlit interface provides an input area, detection controls, and a result display. Additional features, such as example sentences, alternative predictions, and session history, depend on the implemented application.

### 12.7 REST API

Where FastAPI is included, the API provides endpoints for language identification, supported-language information, and health checking. API requests and responses should follow the schemas defined in the implementation.

## 13. Test Cases and Results

The project includes a pytest suite intended to cover language identification, validation, Unicode handling, ambiguous input, and API behavior.

The development notes report a final test run with **62 passed tests and one warning**, completed in approximately four seconds on Python 3.12.3.

This result should be retained as a verified result only if the corresponding test output is available. A new test run on Python 3.14.3 or another environment must be recorded separately.

### 13.1 Test coverage

The intended test coverage includes:

1. English language identification.
2. Kannada language identification.
3. Hindi language identification.
4. Additional supported languages.
5. Empty and whitespace-only input.
6. Numeric-only input.
7. Punctuation-only input.
8. Very short or ambiguous text.
9. Unicode text processing.
10. Unsupported or inconclusive results.
11. API validation and response handling, if the API is included.

Refer to `testing.md` for detailed test cases and output, if that file is present.

### 13.2 Sample language checks

The development notes report the following example predictions:

| Input language | Reported language code | Reported score |
|---|---|---:|
| English | `en` | 0.9952 |
| Kannada | `kn` | 1.0000 |
| Hindi | `hi` | 0.9948 |
| Tamil | `ta` | 1.0000 |
| Telugu | `te` | 1.0000 |
| Malayalam | `ml` | 1.0000 |
| Marathi | `mr` | 0.8889 |
| Bengali | `bn` | 0.9759 |
| Gujarati | `gu` | 1.0000 |
| Punjabi | `pa` | 1.0000 |
| Urdu | `ur` | 1.0000 |
| French | `fr` | 0.9983 |
| German | `de` | 0.9879 |
| Spanish | `es` | 0.9010 |

These values are the results reported in the development notes. They must be checked against the actual execution logs before being presented as verified results.

These examples are individual sentence checks. They are not a benchmark, do not establish general accuracy, and should not be used to claim that the model performs equally well across all texts.

## 14. Results and Discussion

The reported sample checks demonstrate that the selected model can identify several supported languages, including English, Kannada, Hindi, and other Indian and European languages.

However, successful classification of representative sentences does not establish general accuracy. Performance depends on text length, vocabulary, script, language similarity, and whether the input contains multiple languages.

### 14.1 Short-text ambiguity

During development, the single word "नमस्ते" was reportedly classified as Sanskrit with a score of approximately 0.76. This illustrates the difficulty of identifying languages from very short inputs. A word may be shared across languages or provide insufficient evidence for reliable classification.

The system therefore uses warnings and inconclusive-result handling where appropriate.

### 14.2 Mixed-language input

The sentence "I love ಬೆಂಗಳೂರು very much indeed" was reportedly classified as Kannada with a score of 0.9999, despite containing substantial English text.

This is a known failure case, not a successful prediction. It demonstrates that the model can assign a high normalized score to an incorrect label for mixed-language text.

A mixed-script warning may help users recognize the limitation, but it does not correct the prediction. More advanced approaches, such as sentence-level or token-level language identification, would be required to handle such input reliably.

### 14.3 Interpretation of results

The observations indicate that the system is suitable as a basic language-identification demonstration for supported languages and sufficiently informative text. They do not establish reliable performance on all short, ambiguous, transliterated, or mixed-language inputs.

A larger evaluation using a labelled dataset would be necessary to estimate precision, recall, and overall accuracy.

## 15. Limitations

The current approach has the following limitations:

1. Short words and common expressions may be misclassified.
2. Mixed-language sentences may receive an incorrect dominant-language label.
3. Romanized or transliterated Indian languages may not be identified reliably.
4. Languages sharing a writing system can be difficult to distinguish.
5. Normalized model scores are not calibrated probabilities.
6. Only a limited number of languages have been tested individually.
7. No large-scale benchmark evaluation has been performed.
8. Browser-based visual testing must be completed separately from automated tests.
9. Performance may vary with dependency versions and execution environments.

These limitations should be considered when interpreting the output of the application.

## 16. Conclusion

The Language Identification System demonstrates how a pretrained natural language processing model can be integrated into a practical Python application.

The system provides a framework for identifying English, Kannada, Hindi, and other supported languages through a web interface and, where implemented, a REST API. It includes input validation, structured results, uncertainty warnings, and automated tests.

The reported development results show promising behavior on representative sample sentences, but they do not constitute a formal accuracy evaluation. Short and mixed-language text remain important challenges.

The project provides a foundation for further work in multilingual text processing, language identification, and NLP application development.

## 17. Future Enhancements

Possible future improvements include:

1. Sentence-level and token-level identification of mixed-language text.
2. Support for romanized and transliterated Indian languages.
3. Batch processing of text files and document collections.
4. Evaluation on a labelled multilingual benchmark dataset.
5. Calibration and validation of confidence scores.
6. Improved handling of closely related languages.
7. Docker-based deployment and reproducible environments.
8. Deployment of the interface and API to a suitable hosting platform.
9. Improved accessibility, visual design, and multilingual user-interface support.
10. Logging and monitoring that respect user privacy.

## 18. References

1. Cavnar, W. B., & Trenkle, J. M. (1994). *N-Gram-Based Text Categorization*. Proceedings of the Third Symposium on Document Analysis and Information Retrieval (SDAIR-94). Verify the full proceedings details and page range against the original publication before submission.

2. Lui, M., & Baldwin, T. (2012). *langid.py: An Off-the-shelf Language Identification Tool*. Proceedings of the ACL 2012 System Demonstrations, pp. 25–30. Association for Computational Linguistics. https://aclanthology.org/P12-3005/

3. Jauhiainen, T., Lui, M., Zampieri, M., Baldwin, T., & Lindén, K. (2019). *Automatic Language Identification in Texts: A Survey*. Journal of Artificial Intelligence Research, 65, 675–782. https://doi.org/10.1613/jair.1.11675

4. py3langid. *Python package documentation and source code*. https://pypi.org/project/py3langid/ and https://github.com/adbar/py3langid

5. Lingua. *Language detector package documentation*. https://pypi.org/project/lingua-language-detector/

6. Streamlit. *Official documentation*. https://docs.streamlit.io/

7. FastAPI. *Official documentation*. https://fastapi.tiangolo.com/

8. pytest. *Official documentation*. https://docs.pytest.org/

---

