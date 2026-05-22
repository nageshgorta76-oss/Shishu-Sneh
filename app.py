import pandas as pd
import plotly.express as px
import streamlit as st

from chatbot import chatbot_response
from database import delete_baby_data, insert_data, view_data
from growth import build_growth_history, reference_growth_data
from vaccine import VACCINE_SCHEDULE, get_vaccine_guidance


st.set_page_config(
    page_title="Shishu-Sneh",
    page_icon="🍼",
    layout="wide",
)

try:
    ADMIN_PASSWORD = st.secrets["admin_password"]
except Exception:
    ADMIN_PASSWORD = "12345"

st.markdown(
    """
<style>
    .stApp {
        background: linear-gradient(180deg, #fff8fb 0%, #fff5f7 48%, #fffdfd 100%);
    }

    [data-testid="stSidebar"] {
        background: linear-gradient(180deg, #fff0f5 0%, #fff7fa 100%);
    }

    h1, h2, h3 {
        color: #d94b7b;
        font-family: "Trebuchet MS", "Segoe UI", sans-serif;
    }

    .soft-card {
        background: rgba(255, 255, 255, 0.9);
        border: 1px solid #ffd8e6;
        border-radius: 18px;
        padding: 1rem 1.1rem;
        box-shadow: 0 10px 24px rgba(229, 115, 154, 0.12);
        min-height: 132px;
        margin-bottom: 0.75rem;
    }

    .soft-card h4 {
        color: #c43d6a;
        margin: 0 0 0.35rem 0;
    }

    .soft-card p {
        color: #5d4a54;
        margin: 0;
        line-height: 1.55;
    }

    .stButton > button {
        background: linear-gradient(90deg, #ef5b93 0%, #d94b7b 100%);
        color: white;
        border-radius: 12px;
        border: none;
        height: 3rem;
        width: 100%;
        font-weight: 600;
    }
</style>
""",
    unsafe_allow_html=True,
)


def render_soft_card(title, body):
    st.markdown(
        f"""
<div class="soft-card">
    <h4>{title}</h4>
    <p>{body}</p>
</div>
""",
        unsafe_allow_html=True,
    )


def reminder_messages(age_months, language_text):
    guidance = get_vaccine_guidance(age_months)
    due_now = guidance["due_now"]
    due_soon = guidance["due_soon"]

    messages = []

    if due_now:
        vaccine_names = ", ".join(language_text["vaccine_names"][item["code"]] for item in due_now)
        messages.append(
            (
                "error",
                f"{language_text['reminder_due_now_prefix']} {vaccine_names}.",
            )
        )

    if due_soon:
        vaccine_names = ", ".join(language_text["vaccine_names"][item["code"]] for item in due_soon)
        messages.append(
            (
                "warning",
                f"{language_text['reminder_due_soon_prefix']} {vaccine_names}.",
            )
        )

    if not messages:
        messages.append(("success", language_text["no_vaccine_due"]))

    return messages


def vaccine_status_key(age_months, due_month):
    if due_month == 0 and age_months == 0:
        return "due_now"
    if due_month > 0 and due_month <= age_months < due_month + 1:
        return "due_now"
    if 0 < due_month - age_months <= 1:
        return "due_soon"
    if due_month > age_months:
        return "planned"
    return "earlier"


if "show_admin_login" not in st.session_state:
    st.session_state.show_admin_login = False

if "admin_authenticated" not in st.session_state:
    st.session_state.admin_authenticated = False

if "admin_flash_message" not in st.session_state:
    st.session_state.admin_flash_message = ""


translations = {
    "English": {
        "select_language": "Select Language",
        "menu_label": "Menu",
        "title": "🍼 Shishu-Sneh",
        "subtitle": "Soft healthcare support for a baby's first year",
        "modules": "Healthcare Modules",
        "dashboard": "Dashboard",
        "growth": "Growth Tracker",
        "vaccine": "Vaccination Alerts",
        "feeding": "Feeding Guide",
        "milestone": "Milestone Timeline",
        "health": "Health Awareness",
        "ai": "AI Assistant",
        "dashboard_card_1_title": "Mother-Friendly Care",
        "dashboard_card_1_text": "Track monthly weight, height, and important health reminders in one place.",
        "dashboard_card_2_title": "Local Language Support",
        "dashboard_card_2_text": "Every module adapts to English, Hindi, or Kannada for easier understanding at home.",
        "dashboard_card_3_title": "Digital Health Helper",
        "dashboard_card_3_text": "Breastfeeding guidance, vaccine alerts, and milestone checks stay connected across the app.",
        "baby_name": "Baby Name",
        "baby_age": "Baby Age (Months)",
        "weight": "Baby Weight (Kg)",
        "height": "Baby Height (cm)",
        "save": "Save Baby Data",
        "saved": "Baby data saved successfully!",
        "name_warning": "Please enter the baby's name before saving.",
        "weight_metric": "Weight",
        "height_metric": "Height",
        "record_count": "Saved Records",
        "records": "Saved Baby Records",
        "record_empty": "No baby records yet. Save the first record from the dashboard.",
        "record_columns": ["ID", "Name", "Age (Months)", "Weight (Kg)", "Height (cm)"],
        "admin_login": "Admin Login",
        "admin_panel": "Admin Panel",
        "admin_password": "Enter Admin Password",
        "admin_submit": "Login",
        "admin_logout": "Logout",
        "admin_success": "Admin access granted.",
        "admin_error": "Incorrect password.",
        "admin_delete_title": "Delete Baby Data",
        "admin_delete_help": "Select a baby name to delete all saved records for that baby from the database.",
        "admin_select_baby": "Select Baby to Delete",
        "admin_delete_count": "Saved entries for selected baby",
        "admin_delete_button": "Delete Baby Data",
        "admin_delete_success": "Selected baby data was deleted from the database.",
        "admin_delete_empty": "No saved baby data is available to delete.",
        "current_reminders": "Current Vaccine Reminder",
        "month": "Month",
        "age_axis": "Age (Months)",
        "growth_saved_tab": "Saved Growth Trends",
        "growth_reference_tab": "Reference 6-Month Charts",
        "select_baby": "Select Baby",
        "growth_history_info": "Growth charts use the baby records saved in SQLite.",
        "growth_history_empty": "Add at least one saved record to see personal growth trends.",
        "growth_reference_info": "These 6-month charts show a simple reference trend for early growth awareness.",
        "growth_weight_title": "Weight Progress Chart",
        "growth_height_title": "Height Progress Chart",
        "growth_normal": "Growth tracking is active and ready for monthly updates.",
        "latest_age": "Latest Age",
        "latest_weight": "Latest Weight",
        "latest_height": "Latest Height",
        "vaccine_schedule_title": "Immunization Calendar",
        "vaccine_schedule_info": "Vaccine schedule with due time and disease prevention support.",
        "vaccine_age_input": "Check vaccine reminders by baby age (months)",
        "vaccine_columns": ["Vaccine", "Recommended Time", "Disease Prevented", "Status"],
        "vaccine_status": {
            "due_now": "Due now",
            "due_soon": "Due within 1 month",
            "planned": "Planned later",
            "earlier": "Earlier schedule",
        },
        "reminder_due_now_prefix": "Reminder: these vaccines are due now",
        "reminder_due_soon_prefix": "Reminder: these vaccines are coming soon",
        "no_vaccine_due": "No immediate vaccination is due right now.",
        "disease_prevention": "Disease Prevention Information",
        "disease_points": [
            "Polio vaccination helps prevent polio.",
            "BCG helps protect against tuberculosis.",
            "MMR helps protect against measles, mumps, and rubella.",
        ],
        "feeding_intro_title": "Exclusive Breastfeeding Guidance",
        "feeding_intro_text": "Exclusive breastfeeding is recommended for the first 6 months unless a doctor advises otherwise.",
        "feeding_baby_title": "Baby Feeding Tips",
        "feeding_baby_text": "Soft foods after 6 months can include mashed banana, rice cereal, soft fruits, and boiled vegetables.",
        "feeding_mother_title": "Mother Nutrition Tips",
        "feeding_mother_text": "Mothers should drink plenty of water and eat iron, calcium, and protein-rich foods.",
        "feeding_immunity": "Healthy nutrition supports immunity, weight gain, and development.",
        "milestone_intro": "Weekly and monthly developmental milestones can help families notice progress early.",
        "milestones": [
            "6 Weeks - Makes eye contact and begins smiling",
            "8 Weeks - Starts lifting the head during tummy time",
            "16 Weeks - Holds the head more steadily",
            "24 Weeks - Begins rolling or trying to crawl",
            "36 Weeks - Responds to name and familiar voices",
        ],
        "milestone_checklist": "Milestone Checklist",
        "milestone_question": "Is the baby holding their head up?",
        "yes": "Yes",
        "no": "No",
        "milestone_good": "Development looks healthy. Keep encouraging tummy time and interaction.",
        "milestone_watch": "Monitor development and consult a doctor if this continues.",
        "health_card_1_title": "Reduce Infant Mortality Awareness",
        "health_card_1_text": "Vaccination reminders and checkups encourage safer early care decisions.",
        "health_card_2_title": "Prevent Stunting",
        "health_card_2_text": "Nutrition guidance supports healthy growth, breastfeeding, and weight monitoring.",
        "health_card_3_title": "Community Support",
        "health_card_3_text": "Local-language guidance helps families understand health advice more confidently.",
        "health_points": [
            "Vaccinations reduce infant mortality risks.",
            "Proper nutrition helps prevent stunting.",
            "Regular checkups improve child health outcomes.",
            "Breastfeeding supports immunity and development.",
        ],
        "ai_prompt": "Ask your baby care question",
        "ai_button": "Ask AI",
        "ai_helper": "The assistant can answer simple questions about feeding, growth, sleep, fever, and vaccines.",
        "footer": "Healthcare Monitoring System",
        "vaccine_names": {
            "BCG": "BCG",
            "Polio": "Polio",
            "Hepatitis B": "Hepatitis B",
            "DPT": "DPT",
            "MMR": "MMR",
        },
        "vaccine_due_labels": {
            "at_birth": "At Birth",
            "six_weeks": "6 Weeks",
            "ten_weeks": "10 Weeks",
            "nine_months": "9 Months",
        },
        "disease_labels": {
            "tuberculosis": "Tuberculosis",
            "polio": "Polio",
            "hepatitis_b": "Hepatitis B",
            "dpt_combo": "Diphtheria, Pertussis, Tetanus",
            "mmr_combo": "Measles, Mumps, Rubella",
        },
    },
    "Hindi": {
        "select_language": "भाषा चुनें",
        "menu_label": "मेन्यू",
        "title": "🍼 शिशु-स्नेह",
        "subtitle": "बच्चे के पहले वर्ष के लिए सरल और स्नेहपूर्ण स्वास्थ्य सहायता",
        "modules": "स्वास्थ्य मॉड्यूल",
        "dashboard": "डैशबोर्ड",
        "growth": "विकास ट्रैकर",
        "vaccine": "टीकाकरण अलर्ट",
        "feeding": "पोषण मार्गदर्शिका",
        "milestone": "विकास चरण",
        "health": "स्वास्थ्य जागरूकता",
        "ai": "एआई सहायक",
        "dashboard_card_1_title": "मां के लिए आसान देखभाल",
        "dashboard_card_1_text": "मासिक वजन, लंबाई और ज़रूरी स्वास्थ्य रिमाइंडर एक ही जगह पर देखें।",
        "dashboard_card_2_title": "स्थानीय भाषा सहायता",
        "dashboard_card_2_text": "हर मॉड्यूल अंग्रेज़ी, हिंदी या कन्नड़ के अनुसार बदलता है ताकि घर पर समझना आसान हो।",
        "dashboard_card_3_title": "डिजिटल स्वास्थ्य सहायक",
        "dashboard_card_3_text": "स्तनपान मार्गदर्शन, टीका अलर्ट और विकास जांच पूरे ऐप में जुड़े रहते हैं।",
        "baby_name": "बच्चे का नाम",
        "baby_age": "बच्चे की आयु (महीने)",
        "weight": "बच्चे का वजन (किलो)",
        "height": "बच्चे की लंबाई (सेमी)",
        "save": "बच्चे का डेटा सहेजें",
        "saved": "बच्चे का डेटा सफलतापूर्वक सहेजा गया!",
        "name_warning": "सहेजने से पहले कृपया बच्चे का नाम दर्ज करें।",
        "weight_metric": "वजन",
        "height_metric": "लंबाई",
        "record_count": "सहेजे गए रिकॉर्ड",
        "records": "सहेजे गए बच्चे के रिकॉर्ड",
        "record_empty": "अभी कोई रिकॉर्ड नहीं है। डैशबोर्ड से पहला रिकॉर्ड सहेजें।",
        "record_columns": ["आईडी", "नाम", "आयु (महीने)", "वजन (किलो)", "लंबाई (सेमी)"],
        "admin_login": "एडमिन लॉगिन",
        "admin_panel": "एडमिन पैनल",
        "admin_password": "एडमिन पासवर्ड दर्ज करें",
        "admin_submit": "लॉगिन करें",
        "admin_logout": "लॉगआउट",
        "admin_success": "एडमिन एक्सेस मिल गया है।",
        "admin_error": "गलत पासवर्ड।",
        "admin_delete_title": "बच्चे का डेटा हटाएँ",
        "admin_delete_help": "डेटाबेस से उस बच्चे के सभी सहेजे गए रिकॉर्ड हटाने के लिए बच्चे का नाम चुनें।",
        "admin_select_baby": "हटाने के लिए बच्चा चुनें",
        "admin_delete_count": "चुने गए बच्चे की सहेजी गई एंट्रियाँ",
        "admin_delete_button": "बच्चे का डेटा हटाएँ",
        "admin_delete_success": "चुने गए बच्चे का डेटा डेटाबेस से हटा दिया गया है।",
        "admin_delete_empty": "हटाने के लिए कोई सहेजा गया डेटा उपलब्ध नहीं है।",
        "current_reminders": "मौजूदा टीका रिमाइंडर",
        "month": "महीना",
        "age_axis": "आयु (महीने)",
        "growth_saved_tab": "सहेजे गए विकास ट्रेंड",
        "growth_reference_tab": "6 महीने के संदर्भ चार्ट",
        "select_baby": "बच्चा चुनें",
        "growth_history_info": "विकास चार्ट SQLite में सहेजे गए रिकॉर्ड का उपयोग करते हैं।",
        "growth_history_empty": "व्यक्तिगत विकास ट्रेंड देखने के लिए कम से कम एक रिकॉर्ड सहेजें।",
        "growth_reference_info": "ये 6 महीने के चार्ट शुरुआती विकास जागरूकता के लिए एक सरल संदर्भ ट्रेंड दिखाते हैं।",
        "growth_weight_title": "वजन प्रगति चार्ट",
        "growth_height_title": "लंबाई प्रगति चार्ट",
        "growth_normal": "विकास ट्रैकिंग सक्रिय है और मासिक अपडेट के लिए तैयार है।",
        "latest_age": "नवीनतम आयु",
        "latest_weight": "नवीनतम वजन",
        "latest_height": "नवीनतम लंबाई",
        "vaccine_schedule_title": "टीकाकरण कैलेंडर",
        "vaccine_schedule_info": "नियत समय और रोग से सुरक्षा की जानकारी के साथ टीका सूची।",
        "vaccine_age_input": "बच्चे की आयु के आधार पर टीका रिमाइंडर देखें (महीने)",
        "vaccine_columns": ["टीका", "सुझाया गया समय", "किस रोग से बचाव", "स्थिति"],
        "vaccine_status": {
            "due_now": "अभी देय",
            "due_soon": "1 महीने के भीतर देय",
            "planned": "आगे निर्धारित",
            "earlier": "पहले का समय",
        },
        "reminder_due_now_prefix": "याद दिलाना: ये टीके अभी देय हैं",
        "reminder_due_soon_prefix": "याद दिलाना: ये टीके जल्द आने वाले हैं",
        "no_vaccine_due": "अभी कोई तुरंत टीका देय नहीं है।",
        "disease_prevention": "रोग रोकथाम जानकारी",
        "disease_points": [
            "पोलियो का टीका पोलियो से बचाव में मदद करता है।",
            "बीसीजी क्षय रोग से बचाने में मदद करता है।",
            "एमएमआर खसरा, कण्ठमाला और रूबेला से बचाव में मदद करता है।",
        ],
        "feeding_intro_title": "विशेष स्तनपान मार्गदर्शन",
        "feeding_intro_text": "पहले 6 महीनों तक केवल स्तनपान की सलाह दी जाती है, जब तक डॉक्टर कुछ और न कहें।",
        "feeding_baby_title": "बच्चे के भोजन के सुझाव",
        "feeding_baby_text": "6 महीने के बाद मसला हुआ केला, चावल का दलिया, नरम फल और उबली सब्जियां दी जा सकती हैं।",
        "feeding_mother_title": "मां के पोषण के सुझाव",
        "feeding_mother_text": "माताओं को पर्याप्त पानी पीना चाहिए और आयरन, कैल्शियम तथा प्रोटीन युक्त भोजन लेना चाहिए।",
        "feeding_immunity": "स्वस्थ पोषण रोग प्रतिरोधक क्षमता, वजन बढ़ने और विकास में मदद करता है।",
        "milestone_intro": "साप्ताहिक और मासिक विकास चरण परिवारों को बच्चे की प्रगति जल्दी समझने में मदद करते हैं।",
        "milestones": [
            "6 सप्ताह - आंखों से संपर्क बनाता है और मुस्कुराना शुरू करता है",
            "8 सप्ताह - पेट के बल रहने पर सिर उठाने की कोशिश करता है",
            "16 सप्ताह - सिर को अधिक स्थिरता से संभालता है",
            "24 सप्ताह - पलटना या रेंगना शुरू करता है",
            "36 सप्ताह - नाम और परिचित आवाज़ों पर प्रतिक्रिया देता है",
        ],
        "milestone_checklist": "विकास जांच सूची",
        "milestone_question": "क्या बच्चा अपना सिर ऊपर पकड़ पा रहा है?",
        "yes": "हाँ",
        "no": "नहीं",
        "milestone_good": "विकास स्वस्थ लग रहा है। पेट के बल खेलने और बातचीत को जारी रखें।",
        "milestone_watch": "विकास पर ध्यान दें और यह जारी रहे तो डॉक्टर से सलाह लें।",
        "health_card_1_title": "शिशु मृत्यु जागरूकता कम करें",
        "health_card_1_text": "टीका रिमाइंडर और नियमित जांच सुरक्षित शुरुआती देखभाल को बढ़ावा देते हैं।",
        "health_card_2_title": "विकास रुकावट रोकें",
        "health_card_2_text": "पोषण मार्गदर्शन स्वस्थ वृद्धि, स्तनपान और वजन निगरानी में मदद करता है।",
        "health_card_3_title": "समुदाय सहायता",
        "health_card_3_text": "स्थानीय भाषा मार्गदर्शन परिवारों को स्वास्थ्य सलाह बेहतर समझने में मदद करता है।",
        "health_points": [
            "टीकाकरण शिशु मृत्यु के जोखिम को कम करता है।",
            "सही पोषण वृद्धि रुकावट को रोकने में मदद करता है।",
            "नियमित जांच बच्चे के स्वास्थ्य परिणाम बेहतर बनाती है।",
            "स्तनपान रोग प्रतिरोधक क्षमता और विकास को सहारा देता है।",
        ],
        "ai_prompt": "बच्चे की देखभाल से जुड़ा अपना प्रश्न पूछें",
        "ai_button": "एआई से पूछें",
        "ai_helper": "यह सहायक भोजन, विकास, नींद, बुखार और टीकों के बारे में सरल प्रश्नों का उत्तर दे सकता है।",
        "footer": "स्वास्थ्य निगरानी प्रणाली",
        "vaccine_names": {
            "BCG": "बीसीजी",
            "Polio": "पोलियो",
            "Hepatitis B": "हेपेटाइटिस बी",
            "DPT": "डीपीटी",
            "MMR": "एमएमआर",
        },
        "vaccine_due_labels": {
            "at_birth": "जन्म के समय",
            "six_weeks": "6 सप्ताह",
            "ten_weeks": "10 सप्ताह",
            "nine_months": "9 महीने",
        },
        "disease_labels": {
            "tuberculosis": "क्षय रोग",
            "polio": "पोलियो",
            "hepatitis_b": "हेपेटाइटिस बी",
            "dpt_combo": "डिफ्थीरिया, काली खांसी, टिटनेस",
            "mmr_combo": "खसरा, कण्ठमाला, रूबेला",
        },
    },
    "Kannada": {
        "select_language": "ಭಾಷೆಯನ್ನು ಆಯ್ಕೆಮಾಡಿ",
        "menu_label": "ಮೆನು",
        "title": "🍼 ಶಿಶು-ಸ್ನೇಹ",
        "subtitle": "ಮಗುವಿನ ಮೊದಲ ವರ್ಷದ ಆರೈಕೆಗೆ ಮೃದು ಮತ್ತು ಸಹಾಯಕ ಆರೋಗ್ಯ ಮಾರ್ಗದರ್ಶನ",
        "modules": "ಆರೋಗ್ಯ ಘಟಕಗಳು",
        "dashboard": "ಡ್ಯಾಶ್‌ಬೋರ್ಡ್",
        "growth": "ವಿಕಾಸ ಟ್ರ್ಯಾಕರ್",
        "vaccine": "ಲಸಿಕೆ ಎಚ್ಚರಿಕೆಗಳು",
        "feeding": "ಪೋಷಣಾ ಮಾರ್ಗದರ್ಶಿ",
        "milestone": "ವಿಕಾಸ ಹಂತಗಳು",
        "health": "ಆರೋಗ್ಯ ಜಾಗೃತಿ",
        "ai": "ಎಐ ಸಹಾಯಕ",
        "dashboard_card_1_title": "ತಾಯಿಗೆ ಸುಲಭ ಆರೈಕೆ",
        "dashboard_card_1_text": "ಮಾಸಿಕ ತೂಕ, ಎತ್ತರ ಮತ್ತು ಮುಖ್ಯ ಆರೋಗ್ಯ ಜ್ಞಾಪನೆಗಳನ್ನು ಒಂದೇ ಸ್ಥಳದಲ್ಲಿ ನೋಡಿ.",
        "dashboard_card_2_title": "ಸ್ಥಳೀಯ ಭಾಷಾ ಬೆಂಬಲ",
        "dashboard_card_2_text": "ಪ್ರತಿ ಘಟಕವೂ ಇಂಗ್ಲಿಷ್, ಹಿಂದಿ ಅಥವಾ ಕನ್ನಡಕ್ಕೆ ಹೊಂದಿಕೊಳ್ಳುತ್ತದೆ, ಆದ್ದರಿಂದ ಮನೆಯಲ್ಲಿ ಅರ್ಥಮಾಡಿಕೊಳ್ಳಲು ಸುಲಭವಾಗುತ್ತದೆ.",
        "dashboard_card_3_title": "ಡಿಜಿಟಲ್ ಆರೋಗ್ಯ ಸಹಾಯಕ",
        "dashboard_card_3_text": "ತಾಯಿಹಾಲು ಮಾರ್ಗದರ್ಶನ, ಲಸಿಕೆ ಜ್ಞಾಪನೆಗಳು ಮತ್ತು ವಿಕಾಸ ಪರಿಶೀಲನೆಗಳು ಸಂಪೂರ್ಣ ಅಪ್ಲಿಕೇಶನ್‌ನಲ್ಲಿ ಸಂಪರ್ಕದಲ್ಲಿರುತ್ತವೆ.",
        "baby_name": "ಮಗುವಿನ ಹೆಸರು",
        "baby_age": "ಮಗುವಿನ ವಯಸ್ಸು (ತಿಂಗಳು)",
        "weight": "ಮಗುವಿನ ತೂಕ (ಕೆಜಿ)",
        "height": "ಮಗುವಿನ ಎತ್ತರ (ಸೆಂ.ಮೀ)",
        "save": "ಮಗುವಿನ ಡೇಟಾವನ್ನು ಉಳಿಸಿ",
        "saved": "ಮಗುವಿನ ಡೇಟಾ ಯಶಸ್ವಿಯಾಗಿ ಉಳಿಸಲಾಗಿದೆ!",
        "name_warning": "ಉಳಿಸುವ ಮೊದಲು ದಯವಿಟ್ಟು ಮಗುವಿನ ಹೆಸರನ್ನು ನಮೂದಿಸಿ.",
        "weight_metric": "ತೂಕ",
        "height_metric": "ಎತ್ತರ",
        "record_count": "ಉಳಿಸಿದ ದಾಖಲೆಗಳು",
        "records": "ಉಳಿಸಿದ ಮಗುವಿನ ದಾಖಲೆಗಳು",
        "record_empty": "ಇನ್ನೂ ಯಾವುದೇ ದಾಖಲೆಗಳಿಲ್ಲ. ಡ್ಯಾಶ್‌ಬೋರ್ಡ್‌ನಿಂದ ಮೊದಲ ದಾಖಲೆ ಉಳಿಸಿ.",
        "record_columns": ["ಐಡಿ", "ಹೆಸರು", "ವಯಸ್ಸು (ತಿಂಗಳು)", "ತೂಕ (ಕೆಜಿ)", "ಎತ್ತರ (ಸೆಂ.ಮೀ)"],
        "admin_login": "ಆಡ್ಮಿನ್ ಲಾಗಿನ್",
        "admin_panel": "ಆಡ್ಮಿನ್ ಪ್ಯಾನಲ್",
        "admin_password": "ಆಡ್ಮಿನ್ ಪಾಸ್‌ವರ್ಡ್ ನಮೂದಿಸಿ",
        "admin_submit": "ಲಾಗಿನ್ ಮಾಡಿ",
        "admin_logout": "ಲಾಗ್‌ಔಟ್",
        "admin_success": "ಆಡ್ಮಿನ್ ಪ್ರವೇಶ ದೊರಕಿದೆ.",
        "admin_error": "ತಪ್ಪಾದ ಪಾಸ್‌ವರ್ಡ್.",
        "admin_delete_title": "ಮಗುವಿನ ಡೇಟಾವನ್ನು ಅಳಿಸಿ",
        "admin_delete_help": "ಡೇಟಾಬೇಸ್‌ನಿಂದ ಆ ಮಗುವಿನ ಎಲ್ಲಾ ಉಳಿಸಿದ ದಾಖಲೆಗಳನ್ನು ಅಳಿಸಲು ಮಗುವಿನ ಹೆಸರನ್ನು ಆಯ್ಕೆಮಾಡಿ.",
        "admin_select_baby": "ಅಳಿಸಲು ಮಗುವನ್ನು ಆಯ್ಕೆಮಾಡಿ",
        "admin_delete_count": "ಆಯ್ಕೆ ಮಾಡಿದ ಮಗುವಿನ ಉಳಿಸಿದ ನಮೂದುಗಳು",
        "admin_delete_button": "ಮಗುವಿನ ಡೇಟಾವನ್ನು ಅಳಿಸಿ",
        "admin_delete_success": "ಆಯ್ಕೆ ಮಾಡಿದ ಮಗುವಿನ ಡೇಟಾವನ್ನು ಡೇಟಾಬೇಸ್‌ನಿಂದ ಅಳಿಸಲಾಗಿದೆ.",
        "admin_delete_empty": "ಅಳಿಸಲು ಯಾವುದೇ ಉಳಿಸಿದ ಡೇಟಾ ಇಲ್ಲ.",
        "current_reminders": "ಪ್ರಸ್ತುತ ಲಸಿಕೆ ಜ್ಞಾಪನೆ",
        "month": "ತಿಂಗಳು",
        "age_axis": "ವಯಸ್ಸು (ತಿಂಗಳು)",
        "growth_saved_tab": "ಉಳಿಸಿದ ವಿಕಾಸ ಟ್ರೆಂಡ್‌ಗಳು",
        "growth_reference_tab": "6 ತಿಂಗಳ ಉಲ್ಲೇಖ ಚಾರ್ಟ್‌ಗಳು",
        "select_baby": "ಮಗುವನ್ನು ಆಯ್ಕೆಮಾಡಿ",
        "growth_history_info": "ವಿಕಾಸ ಚಾರ್ಟ್‌ಗಳು SQLite ನಲ್ಲಿ ಉಳಿಸಿದ ದಾಖಲೆಗಳನ್ನು ಬಳಸುತ್ತವೆ.",
        "growth_history_empty": "ವೈಯಕ್ತಿಕ ವಿಕಾಸ ಟ್ರೆಂಡ್ ನೋಡಲು ಕನಿಷ್ಠ ಒಂದು ದಾಖಲೆ ಉಳಿಸಿ.",
        "growth_reference_info": "ಈ 6 ತಿಂಗಳ ಚಾರ್ಟ್‌ಗಳು ಆರಂಭಿಕ ವಿಕಾಸ ಜಾಗೃತಿಗಾಗಿ ಸರಳ ಉಲ್ಲೇಖ ಧೋರಣೆಯನ್ನು ತೋರಿಸುತ್ತವೆ.",
        "growth_weight_title": "ತೂಕ ಪ್ರಗತಿ ಚಾರ್ಟ್",
        "growth_height_title": "ಎತ್ತರ ಪ್ರಗತಿ ಚಾರ್ಟ್",
        "growth_normal": "ವಿಕಾಸ ಟ್ರ್ಯಾಕಿಂಗ್ ಸಕ್ರಿಯವಾಗಿದೆ ಮತ್ತು ಮಾಸಿಕ ನವೀಕರಣಗಳಿಗೆ ಸಿದ್ಧವಾಗಿದೆ.",
        "latest_age": "ಇತ್ತೀಚಿನ ವಯಸ್ಸು",
        "latest_weight": "ಇತ್ತೀಚಿನ ತೂಕ",
        "latest_height": "ಇತ್ತೀಚಿನ ಎತ್ತರ",
        "vaccine_schedule_title": "ಲಸಿಕಾ ಕ್ಯಾಲೆಂಡರ್",
        "vaccine_schedule_info": "ನಿಗದಿತ ಸಮಯ ಮತ್ತು ತಡೆಯುವ ರೋಗದ ಮಾಹಿತಿಯೊಂದಿಗೆ ಲಸಿಕೆ ಪಟ್ಟಿ.",
        "vaccine_age_input": "ಮಗುವಿನ ವಯಸ್ಸಿನ ಆಧಾರದ ಮೇಲೆ ಲಸಿಕೆ ಜ್ಞಾಪನೆಗಳನ್ನು ನೋಡಿ (ತಿಂಗಳು)",
        "vaccine_columns": ["ಲಸಿಕೆ", "ಶಿಫಾರಸು ಮಾಡಿದ ಸಮಯ", "ತಡೆಯುವ ರೋಗ", "ಸ್ಥಿತಿ"],
        "vaccine_status": {
            "due_now": "ಈಗ ಕೊಡಬೇಕು",
            "due_soon": "1 ತಿಂಗಳೊಳಗೆ ಕೊಡಬೇಕು",
            "planned": "ಮುಂದೆ ನಿಗದಿಯಾಗಿದೆ",
            "earlier": "ಹಿಂದಿನ ವೇಳಾಪಟ್ಟಿ",
        },
        "reminder_due_now_prefix": "ಜ್ಞಾಪನೆ: ಈ ಲಸಿಕೆಗಳು ಈಗ ಕೊಡಬೇಕಾಗಿದೆ",
        "reminder_due_soon_prefix": "ಜ್ಞಾಪನೆ: ಈ ಲಸಿಕೆಗಳು ಶೀಘ್ರದಲ್ಲೇ ಬರಲಿವೆ",
        "no_vaccine_due": "ಈಗ ತಕ್ಷಣ ಕೊಡಬೇಕಾದ ಲಸಿಕೆ ಇಲ್ಲ.",
        "disease_prevention": "ರೋಗ ತಡೆ ಮಾಹಿತಿ",
        "disease_points": [
            "ಪೋಲಿಯೋ ಲಸಿಕೆ ಪೋಲಿಯೋ ತಡೆಗಟ್ಟಲು ಸಹಾಯ ಮಾಡುತ್ತದೆ.",
            "ಬಿಸಿಜಿ ಕ್ಷಯರೋಗದಿಂದ ರಕ್ಷಿಸಲು ಸಹಾಯ ಮಾಡುತ್ತದೆ.",
            "ಎಂಎಂಆರ್ ಕಾಸೆ, ಮಂಪ್ಸ್ ಮತ್ತು ರುಬೆಲ್ಲಾ ತಡೆಗಟ್ಟಲು ಸಹಾಯ ಮಾಡುತ್ತದೆ.",
        ],
        "feeding_intro_title": "ವಿಶೇಷ ತಾಯಿಹಾಲು ಮಾರ್ಗದರ್ಶನ",
        "feeding_intro_text": "ವೈದ್ಯರು ಬೇರೆ ಸಲಹೆ ನೀಡದಿದ್ದರೆ ಮೊದಲ 6 ತಿಂಗಳು ಕೇವಲ ತಾಯಿಹಾಲು ನೀಡುವುದು ಶಿಫಾರಸು ಮಾಡಲಾಗುತ್ತದೆ.",
        "feeding_baby_title": "ಮಗುವಿನ ಆಹಾರ ಸಲಹೆಗಳು",
        "feeding_baby_text": "6 ತಿಂಗಳ ನಂತರ ನುರಿದ ಬಾಳೆಹಣ್ಣು, ಅಕ್ಕಿ ಸೀರಿಯಲ್, ಮೃದುವಾದ ಹಣ್ಣುಗಳು ಮತ್ತು ಉಂಡಾದ ತರಕಾರಿಗಳನ್ನು ನೀಡಬಹುದು.",
        "feeding_mother_title": "ತಾಯಿಯ ಪೋಷಣಾ ಸಲಹೆಗಳು",
        "feeding_mother_text": "ತಾಯಂದಿರು ಸಾಕಷ್ಟು ನೀರು ಕುಡಿಯಬೇಕು ಮತ್ತು ಐರನ್, ಕ್ಯಾಲ್ಸಿಯಂ ಹಾಗೂ ಪ್ರೋಟೀನ್ ಸಮೃದ್ಧ ಆಹಾರ ಸೇವಿಸಬೇಕು.",
        "feeding_immunity": "ಆರೋಗ್ಯಕರ ಪೋಷಣೆ ರೋಗನಿರೋಧಕ ಶಕ್ತಿ, ತೂಕ ಹೆಚ್ಚಳ ಮತ್ತು ವಿಕಾಸಕ್ಕೆ ಸಹಾಯ ಮಾಡುತ್ತದೆ.",
        "milestone_intro": "ವಾರದ ಮತ್ತು ತಿಂಗಳ ವಿಕಾಸ ಹಂತಗಳು ಕುಟುಂಬಗಳಿಗೆ ಮಗುವಿನ ಪ್ರಗತಿಯನ್ನು ಬೇಗ ಗಮನಿಸಲು ಸಹಾಯ ಮಾಡುತ್ತವೆ.",
        "milestones": [
            "6 ವಾರಗಳು - ಕಣ್ಣು ಸಂಪರ್ಕ ಮಾಡುತ್ತದೆ ಮತ್ತು ನಗಲು ಪ್ರಾರಂಭಿಸುತ್ತದೆ",
            "8 ವಾರಗಳು - ಹೊಟ್ಟೆಯ ಮೇಲೆ ಇರುವಾಗ ತಲೆಯನ್ನು ಎತ್ತಲು ಪ್ರಯತ್ನಿಸುತ್ತದೆ",
            "16 ವಾರಗಳು - ತಲೆಯನ್ನು ಹೆಚ್ಚು ಸ್ಥಿರವಾಗಿ ಹಿಡಿಯುತ್ತದೆ",
            "24 ವಾರಗಳು - ಉರುಳಲು ಅಥವಾ ಹಾವರಿಸಲು ಪ್ರಾರಂಭಿಸುತ್ತದೆ",
            "36 ವಾರಗಳು - ಹೆಸರು ಮತ್ತು ಪರಿಚಿತ ಧ್ವನಿಗೆ ಪ್ರತಿಕ್ರಿಯಿಸುತ್ತದೆ",
        ],
        "milestone_checklist": "ವಿಕಾಸ ಪರಿಶೀಲನಾ ಪಟ್ಟಿ",
        "milestone_question": "ಮಗು ತಲೆಯನ್ನು ಮೇಲಕ್ಕೆ ಹಿಡಿಯುತ್ತಿದೆಯೇ?",
        "yes": "ಹೌದು",
        "no": "ಇಲ್ಲ",
        "milestone_good": "ವಿಕಾಸ ಆರೋಗ್ಯಕರವಾಗಿ ಕಾಣುತ್ತಿದೆ. ಟಮ್ಮಿ ಟೈಮ್ ಮತ್ತು ಸಂವಹನವನ್ನು ಮುಂದುವರಿಸಿ.",
        "milestone_watch": "ವಿಕಾಸವನ್ನು ಗಮನಿಸಿ ಮತ್ತು ಇದು ಮುಂದುವರಿದರೆ ವೈದ್ಯರನ್ನು ಸಂಪರ್ಕಿಸಿ.",
        "health_card_1_title": "ಶಿಶು ಮರಣ ಜಾಗೃತಿ ಕಡಿಮೆ ಮಾಡಿ",
        "health_card_1_text": "ಲಸಿಕೆ ಜ್ಞಾಪನೆಗಳು ಮತ್ತು ನಿಯಮಿತ ತಪಾಸಣೆಗಳು ಸುರಕ್ಷಿತ ಆರಂಭಿಕ ಆರೈಕೆಗೆ ಉತ್ತೇಜನ ನೀಡುತ್ತವೆ.",
        "health_card_2_title": "ಬೆಳವಣಿಗೆಯ ತೊಂದರೆ ತಡೆ",
        "health_card_2_text": "ಪೋಷಣಾ ಮಾರ್ಗದರ್ಶನ ಆರೋಗ್ಯಕರ ಬೆಳವಣಿಗೆ, ತಾಯಿಹಾಲು ಮತ್ತು ತೂಕ ನಿಗಾವಳಿಗೆ ಸಹಾಯ ಮಾಡುತ್ತದೆ.",
        "health_card_3_title": "ಸಮುದಾಯ ಬೆಂಬಲ",
        "health_card_3_text": "ಸ್ಥಳೀಯ ಭಾಷೆಯ ಮಾರ್ಗದರ್ಶನ ಕುಟುಂಬಗಳಿಗೆ ಆರೋಗ್ಯ ಸಲಹೆಯನ್ನು ಹೆಚ್ಚು ವಿಶ್ವಾಸದಿಂದ ಅರ್ಥಮಾಡಿಕೊಳ್ಳಲು ಸಹಾಯ ಮಾಡುತ್ತದೆ.",
        "health_points": [
            "ಲಸಿಕೆಗಳು ಶಿಶು ಮರಣದ ಅಪಾಯವನ್ನು ಕಡಿಮೆ ಮಾಡುತ್ತವೆ.",
            "ಸರಿಯಾದ ಪೋಷಣೆ ಬೆಳವಣಿಗೆಯ ತೊಂದರೆಯನ್ನು ತಡೆಯಲು ಸಹಾಯ ಮಾಡುತ್ತದೆ.",
            "ನಿಯಮಿತ ತಪಾಸಣೆಗಳು ಮಗುವಿನ ಆರೋಗ್ಯ ಫಲಿತಾಂಶಗಳನ್ನು ಉತ್ತಮಗೊಳಿಸುತ್ತವೆ.",
            "ತಾಯಿಹಾಲು ರೋಗನಿರೋಧಕ ಶಕ್ತಿ ಮತ್ತು ವಿಕಾಸಕ್ಕೆ ಬೆಂಬಲ ನೀಡುತ್ತದೆ.",
        ],
        "ai_prompt": "ಮಗು ನೋಡಿಕೊಳ್ಳುವ ಬಗ್ಗೆ ನಿಮ್ಮ ಪ್ರಶ್ನೆಯನ್ನು ಕೇಳಿ",
        "ai_button": "ಎಐಗೆ ಕೇಳಿ",
        "ai_helper": "ಈ ಸಹಾಯಕ ಆಹಾರ, ವಿಕಾಸ, ನಿದ್ರೆ, ಜ್ವರ ಮತ್ತು ಲಸಿಕೆಗಳ ಬಗ್ಗೆ ಸರಳ ಪ್ರಶ್ನೆಗಳಿಗೆ ಉತ್ತರಿಸಬಹುದು.",
        "footer": "ಆರೋಗ್ಯ ನಿಗಾವಳಿ ವ್ಯವಸ್ಥೆ",
        "vaccine_names": {
            "BCG": "ಬಿಸಿಜಿ",
            "Polio": "ಪೋಲಿಯೋ",
            "Hepatitis B": "ಹೆಪಟೈಟಿಸ್ ಬಿ",
            "DPT": "ಡಿಪಿಟಿ",
            "MMR": "ಎಂಎಂಆರ್",
        },
        "vaccine_due_labels": {
            "at_birth": "ಜನನ ಸಮಯದಲ್ಲಿ",
            "six_weeks": "6 ವಾರಗಳು",
            "ten_weeks": "10 ವಾರಗಳು",
            "nine_months": "9 ತಿಂಗಳು",
        },
        "disease_labels": {
            "tuberculosis": "ಕ್ಷಯರೋಗ",
            "polio": "ಪೋಲಿಯೋ",
            "hepatitis_b": "ಹೆಪಟೈಟಿಸ್ ಬಿ",
            "dpt_combo": "ಡಿಫ್ತೀರಿಯಾ, ಪೆರ್ಟುಸಿಸ್, ಟೆಟನಸ್",
            "mmr_combo": "ಕಾಸೆ, ಮಂಪ್ಸ್, ರುಬೆಲ್ಲಾ",
        },
    },
}


current_language = st.session_state.get("language", "English")

language = st.sidebar.selectbox(
    translations[current_language]["select_language"],
    ["English", "Hindi", "Kannada"],
    key="language",
)

t = translations[language]

records = view_data()
records_df = pd.DataFrame(records, columns=["id", "name", "age", "weight", "height"])

st.title(t["title"])
st.subheader(t["subtitle"])

st.sidebar.title(t["modules"])

menu = st.sidebar.selectbox(
    t["menu_label"],
    [
        t["dashboard"],
        t["growth"],
        t["vaccine"],
        t["feeding"],
        t["milestone"],
        t["health"],
        t["ai"],
    ],
)

if st.sidebar.button(t["admin_login"]):
    st.session_state.show_admin_login = not st.session_state.show_admin_login

if st.session_state.show_admin_login or st.session_state.admin_authenticated:
    st.sidebar.markdown("---")
    st.sidebar.subheader(t["admin_panel"])

    if not st.session_state.admin_authenticated:
        admin_password_input = st.sidebar.text_input(
            t["admin_password"],
            key="admin_password_input",
        )

        if st.sidebar.button(t["admin_submit"]):
            if admin_password_input == ADMIN_PASSWORD:
                st.session_state.admin_authenticated = True
                st.sidebar.success(t["admin_success"])
                st.rerun()
            else:
                st.sidebar.error(t["admin_error"])
    else:
        st.sidebar.success(t["admin_success"])
        if st.sidebar.button(t["admin_logout"]):
            st.session_state.admin_authenticated = False
            st.session_state.show_admin_login = False
            st.session_state.pop("admin_password_input", None)
            st.rerun()

if menu == t["dashboard"]:
    st.header(t["dashboard"])

    if st.session_state.admin_flash_message:
        st.success(st.session_state.admin_flash_message)
        st.session_state.admin_flash_message = ""

    card_col1, card_col2, card_col3 = st.columns(3)
    with card_col1:
        render_soft_card(t["dashboard_card_1_title"], t["dashboard_card_1_text"])
    with card_col2:
        render_soft_card(t["dashboard_card_2_title"], t["dashboard_card_2_text"])
    with card_col3:
        render_soft_card(t["dashboard_card_3_title"], t["dashboard_card_3_text"])

    baby_name = st.text_input(t["baby_name"])
    baby_age = st.slider(t["baby_age"], 0, 12, 6)
    baby_weight = st.number_input(t["weight"], min_value=1.0, max_value=15.0, value=6.5, step=0.1)
    baby_height = st.number_input(t["height"], min_value=30.0, max_value=100.0, value=65.0, step=0.5)

    if st.button(t["save"]):
        if baby_name.strip():
            insert_data(baby_name.strip(), baby_age, baby_weight, baby_height)
            st.success(t["saved"])
            records = view_data()
            records_df = pd.DataFrame(records, columns=["id", "name", "age", "weight", "height"])
        else:
            st.warning(t["name_warning"])

    metric_col1, metric_col2, metric_col3 = st.columns(3)
    with metric_col1:
        st.metric(t["weight_metric"], f"{baby_weight:.1f} Kg")
    with metric_col2:
        st.metric(t["height_metric"], f"{baby_height:.1f} cm")
    with metric_col3:
        st.metric(t["record_count"], len(records_df))

    st.subheader(t["current_reminders"])
    for message_type, message in reminder_messages(baby_age, t):
        getattr(st, message_type)(message)

    st.subheader(t["records"])
    if records_df.empty:
        st.info(t["record_empty"])
    else:
        display_df = records_df.copy()
        display_df.columns = t["record_columns"]
        st.dataframe(display_df, use_container_width=True, hide_index=True)

    if st.session_state.admin_authenticated:
        st.markdown("---")
        st.subheader(t["admin_delete_title"])

        if records_df.empty:
            st.info(t["admin_delete_empty"])
        else:
            baby_names = sorted(records_df["name"].dropna().unique().tolist())
            delete_baby_name = st.selectbox(
                t["admin_select_baby"],
                baby_names,
                key="delete_baby_name",
            )

            delete_count = int((records_df["name"] == delete_baby_name).sum())
            st.metric(t["admin_delete_count"], delete_count)
            st.warning(t["admin_delete_help"])

            if st.button(t["admin_delete_button"]):
                delete_baby_data(delete_baby_name)
                st.session_state.admin_flash_message = t["admin_delete_success"]
                st.rerun()

elif menu == t["growth"]:
    st.header(t["growth"])
    st.info(t["growth_normal"])

    saved_tab, reference_tab = st.tabs([t["growth_saved_tab"], t["growth_reference_tab"]])

    with saved_tab:
        st.caption(t["growth_history_info"])
        if records_df.empty:
            st.info(t["growth_history_empty"])
        else:
            baby_names = sorted(records_df["name"].dropna().unique().tolist())
            selected_baby = st.selectbox(t["select_baby"], baby_names)
            history_df = build_growth_history(records, selected_baby)

            if not history_df.empty:
                latest_row = history_df.iloc[-1]
                metric_col1, metric_col2, metric_col3 = st.columns(3)
                with metric_col1:
                    st.metric(t["latest_age"], str(int(latest_row["age"])))
                with metric_col2:
                    st.metric(t["latest_weight"], f"{latest_row['weight']:.1f} Kg")
                with metric_col3:
                    st.metric(t["latest_height"], f"{latest_row['height']:.1f} cm")

                weight_plot = history_df.rename(
                    columns={
                        "age": t["age_axis"],
                        "weight": t["weight_metric"],
                    }
                )
                weight_fig = px.line(
                    weight_plot,
                    x=t["age_axis"],
                    y=t["weight_metric"],
                    markers=True,
                    title=t["growth_weight_title"],
                )
                st.plotly_chart(weight_fig, use_container_width=True)

                height_plot = history_df.rename(
                    columns={
                        "age": t["age_axis"],
                        "height": t["height_metric"],
                    }
                )
                height_fig = px.line(
                    height_plot,
                    x=t["age_axis"],
                    y=t["height_metric"],
                    markers=True,
                    title=t["growth_height_title"],
                )
                st.plotly_chart(height_fig, use_container_width=True)

    with reference_tab:
        st.caption(t["growth_reference_info"])
        reference_df = reference_growth_data()

        weight_reference = reference_df.rename(
            columns={
                "month": t["month"],
                "weight": t["weight_metric"],
            }
        )
        weight_ref_fig = px.line(
            weight_reference,
            x=t["month"],
            y=t["weight_metric"],
            markers=True,
            title=t["growth_weight_title"],
        )
        st.plotly_chart(weight_ref_fig, use_container_width=True)

        height_reference = reference_df.rename(
            columns={
                "month": t["month"],
                "height": t["height_metric"],
            }
        )
        height_ref_fig = px.line(
            height_reference,
            x=t["month"],
            y=t["height_metric"],
            markers=True,
            title=t["growth_height_title"],
        )
        st.plotly_chart(height_ref_fig, use_container_width=True)

elif menu == t["vaccine"]:
    st.header(t["vaccine"])
    st.subheader(t["vaccine_schedule_title"])
    st.caption(t["vaccine_schedule_info"])

    vaccine_age = st.slider(t["vaccine_age_input"], 0, 12, 2)

    vaccine_rows = []
    for vaccine in VACCINE_SCHEDULE:
        status_key = vaccine_status_key(vaccine_age, vaccine["due_month"])
        vaccine_rows.append(
            {
                t["vaccine_columns"][0]: t["vaccine_names"][vaccine["code"]],
                t["vaccine_columns"][1]: t["vaccine_due_labels"][vaccine["due_label"]],
                t["vaccine_columns"][2]: t["disease_labels"][vaccine["disease_key"]],
                t["vaccine_columns"][3]: t["vaccine_status"][status_key],
            }
        )

    st.dataframe(pd.DataFrame(vaccine_rows), use_container_width=True, hide_index=True)

    for message_type, message in reminder_messages(vaccine_age, t):
        getattr(st, message_type)(message)

    st.subheader(t["disease_prevention"])
    for point in t["disease_points"]:
        st.write(f"- {point}")

elif menu == t["feeding"]:
    st.header(t["feeding"])

    card_col1, card_col2, card_col3 = st.columns(3)
    with card_col1:
        render_soft_card(t["feeding_intro_title"], t["feeding_intro_text"])
    with card_col2:
        render_soft_card(t["feeding_baby_title"], t["feeding_baby_text"])
    with card_col3:
        render_soft_card(t["feeding_mother_title"], t["feeding_mother_text"])

    st.success(t["feeding_immunity"])

elif menu == t["milestone"]:
    st.header(t["milestone"])
    st.write(t["milestone_intro"])

    for milestone in t["milestones"]:
        st.success(milestone)

    st.subheader(t["milestone_checklist"])
    head_control = st.radio(
        t["milestone_question"],
        [t["yes"], t["no"]],
        horizontal=True,
    )

    if head_control == t["yes"]:
        st.success(t["milestone_good"])
    else:
        st.warning(t["milestone_watch"])

elif menu == t["health"]:
    st.header(t["health"])

    card_col1, card_col2, card_col3 = st.columns(3)
    with card_col1:
        render_soft_card(t["health_card_1_title"], t["health_card_1_text"])
    with card_col2:
        render_soft_card(t["health_card_2_title"], t["health_card_2_text"])
    with card_col3:
        render_soft_card(t["health_card_3_title"], t["health_card_3_text"])

    for point in t["health_points"]:
        st.info(point)

elif menu == t["ai"]:
    st.header(t["ai"])
    st.caption(t["ai_helper"])

    question = st.text_input(t["ai_prompt"])
    if st.button(t["ai_button"]):
        response = chatbot_response(question, language)
        st.success(response)

st.markdown("---")
st.caption(t["footer"])
