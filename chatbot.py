import os

from dotenv import load_dotenv

load_dotenv()

api_key = os.getenv("GEMINI_API_KEY")







def chatbot_response(question, language="English"):
    if not question or not question.strip():
        empty_responses = {
            "English": "Please type a baby care question first.",
            "Hindi": "कृपया पहले बच्चे की देखभाल से जुड़ा प्रश्न लिखें।",
            "Kannada": "ದಯವಿಟ್ಟು ಮೊದಲು ಮಗುವಿನ ಆರೈಕೆ ಕುರಿತು ಪ್ರಶ್ನೆಯನ್ನು ಬರೆಯಿರಿ.",
        }
        return empty_responses.get(language, empty_responses["English"])

    normalized_question = question.strip().lower()

    language_rules = {
        "English": [
            (
                ["food", "diet", "nutrition", "eat", "feeding"],
                "Recommended foods include mashed banana, rice cereal, boiled potato, and other soft fruits.",
            ),
            (
                ["breastfeeding", "breastfeed", "milk"],
                "Exclusive breastfeeding is recommended for the first 6 months unless a doctor advises otherwise.",
            ),
            (
                ["fever", "temperature"],
                "Monitor the temperature, keep the baby hydrated, and consult a doctor if the fever continues.",
            ),
            (
                ["vaccine", "vaccination", "polio", "mmr"],
                "Vaccines protect babies from diseases like polio, tuberculosis, and measles.",
            ),
            (
                ["weight", "growth", "height"],
                "Healthy growth depends on proper nutrition, good sleep, routine vaccination, and breastfeeding.",
            ),
            (
                ["sleep", "nap"],
                "Babies usually sleep 12 to 16 hours a day in the first year.",
            ),
        ],
        "Hindi": [
            (
                ["food", "diet", "nutrition", "feeding", "खाना", "भोजन", "आहार"],
                "सुझाए गए भोजन में मसला हुआ केला, चावल का दलिया, उबला आलू और नरम फल शामिल हैं।",
            ),
            (
                ["breastfeeding", "breastfeed", "milk", "स्तनपान", "दूध"],
                "पहले 6 महीनों तक केवल स्तनपान की सलाह दी जाती है, जब तक डॉक्टर कुछ और न कहें।",
            ),
            (
                ["fever", "temperature", "बुखार", "तापमान"],
                "तापमान पर नज़र रखें, बच्चे को पर्याप्त तरल दें और बुखार बना रहे तो डॉक्टर से सलाह लें।",
            ),
            (
                ["vaccine", "vaccination", "टीका", "टीकाकरण", "पोलियो", "एमएमआर"],
                "टीके बच्चों को पोलियो, तपेदिक और खसरे जैसी बीमारियों से बचाते हैं।",
            ),
            (
                ["weight", "growth", "height", "वजन", "विकास", "लंबाई"],
                "स्वस्थ विकास के लिए सही पोषण, अच्छी नींद, नियमित टीकाकरण और स्तनपान बहुत महत्वपूर्ण हैं।",
            ),
            (
                ["sleep", "nap", "नींद", "सोना"],
                "पहले वर्ष में बच्चे सामान्यतः दिन में 12 से 16 घंटे तक सोते हैं।",
            ),
        ],
        "Kannada": [
            (
                ["food", "diet", "nutrition", "feeding", "ಆಹಾರ", "ತಿಂಡಿ", "ಊಟ"],
                "ಶಿಫಾರಸು ಮಾಡಿದ ಆಹಾರಗಳಲ್ಲಿ ನುರಿದ ಬಾಳೆಹಣ್ಣು, ಅಕ್ಕಿ ಸೀರಿಯಲ್, ಉಂಡಾದ ಆಲೂಗಡ್ಡೆ ಮತ್ತು ಮೃದುವಾದ ಹಣ್ಣುಗಳು ಸೇರಿವೆ.",
            ),
            (
                ["breastfeeding", "breastfeed", "milk", "ತಾಯಿಹಾಲು", "ಹಾಲು"],
                "ವೈದ್ಯರು ಬೇರೆ ಸಲಹೆ ನೀಡದಿದ್ದರೆ ಮೊದಲ 6 ತಿಂಗಳು ಕೇವಲ ತಾಯಿಹಾಲು ನೀಡುವುದು ಶಿಫಾರಸು ಮಾಡಲಾಗುತ್ತದೆ.",
            ),
            (
                ["fever", "temperature", "ಜ್ವರ", "ತಾಪಮಾನ"],
                "ತಾಪಮಾನವನ್ನು ಗಮನಿಸಿ, ಮಗುವಿಗೆ ಸಾಕಷ್ಟು ದ್ರವ ನೀಡಿ, ಜ್ವರ ಮುಂದುವರಿದರೆ ವೈದ್ಯರನ್ನು ಸಂಪರ್ಕಿಸಿ.",
            ),
            (
                ["vaccine", "vaccination", "ಲಸಿಕೆ", "ಪೋಲಿಯೋ", "ಎಂಎಂಆರ್"],
                "ಲಸಿಕೆಗಳು ಮಕ್ಕಳನ್ನು ಪೋಲಿಯೋ, ಕ್ಷಯರೋಗ ಮತ್ತು ಕಾಸೆ ರೋಗದಂತಹ ಅನಾರೋಗ್ಯಗಳಿಂದ ರಕ್ಷಿಸುತ್ತವೆ.",
            ),
            (
                ["weight", "growth", "height", "ತೂಕ", "ವಿಕಾಸ", "ಎತ್ತರ"],
                "ಆರೋಗ್ಯಕರ ವಿಕಾಸಕ್ಕೆ ಸರಿಯಾದ ಪೋಷಣೆ, ಉತ್ತಮ ನಿದ್ರೆ, ನಿಯಮಿತ ಲಸಿಕೆಗಳು ಮತ್ತು ತಾಯಿಹಾಲು ಬಹಳ ಮುಖ್ಯವಾಗಿವೆ.",
            ),
            (
                ["sleep", "nap", "ನಿದ್ರೆ", "ಮಲಗು"],
                "ಮೊದಲ ವರ್ಷದ ಅವಧಿಯಲ್ಲಿ ಮಕ್ಕಳು ಸಾಮಾನ್ಯವಾಗಿ ದಿನಕ್ಕೆ 12 ರಿಂದ 16 ಗಂಟೆಗಳವರೆಗೆ ನಿದ್ರಿಸುತ್ತಾರೆ.",
            ),
        ],
    }

    fallback_responses = {
        "English": "Please consult a pediatrician for detailed medical advice.",
        "Hindi": "विस्तृत चिकित्सीय सलाह के लिए कृपया बाल रोग विशेषज्ञ से संपर्क करें।",
        "Kannada": "ವಿಸ್ತೃತ ವೈದ್ಯಕೀಯ ಸಲಹೆಗಾಗಿ ದಯವಿಟ್ಟು ಮಕ್ಕಳ ವೈದ್ಯರನ್ನು ಸಂಪರ್ಕಿಸಿ.",
    }

    for keywords, response in language_rules.get(language, language_rules["English"]):
        if any(keyword in normalized_question for keyword in keywords):
            return response

    return fallback_responses.get(language, fallback_responses["English"])
