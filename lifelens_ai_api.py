'''
Created on July 09 , 2025
Final Combined Flask API with Gemini Flash for:
1. Lifestyle Survey (with HTML formatting)
2. Symptom Diagnostic (also with formatting now)
'''

from dotenv import load_dotenv
load_dotenv()

from flask import Flask, request, jsonify
import os
import traceback
import google.generativeai as genai
import re

app = Flask(__name__)

# Load Gemini API key
gemini_key = os.getenv("GEMINI_API_KEY")
if not gemini_key:
    raise RuntimeError("❌ GEMINI_API_KEY not set in .env file!")

# Configure Gemini
genai.configure(api_key=gemini_key)
model = genai.GenerativeModel("gemini-1.5-flash", generation_config=genai.types.GenerationConfig(temperature=0))

# Format Gemini output to styled HTML
def format_response_to_html(text):
    # 🔍 Step 1: Extract rating (e.g., "3/5") and save explanation text
    rating_match = re.search(r"\b([1-5])/5\.\s*(.+)", text)
    rating = rating_match.group(1) if rating_match else None
    explanation = rating_match.group(2).strip() if rating_match else ""

    # 🔧 Step 2: Remove the full "3/5. Explanation..." line from original text
    text = re.sub(r"\b[1-5]/5\..+?(?=<br>|$)", "", text, flags=re.DOTALL)

    # 🎨 Step 3: Format section headers like "1. 👋 Greeting:"
    text = re.sub(r"^(\d+\.\s+[^\n:]+:)", r"<h3 style='color: #22c55e; font-weight: bold;'>\1</h3>", text, flags=re.MULTILINE)

    # 💬 Step 4: Clean up bullet symbols
    text = re.sub(r"(?m)^\s*[\-\\•]\s", "", text)

    # 💥 Step 5: Format bold like *this*
    text = re.sub(r"\\(.?)\\*", r"<span class='sub-heading'>\1</span>", text)

    # 👋 Step 6: Format greeting line
    text = re.sub(
    r'^"(Hi .*?)"$',
    r"<p style='color: #f8fafc; font-weight: bold; font-size: 1.1rem;'>\1</p>",
    text,
    flags=re.MULTILINE
)


    # 📊 Step 7: Rating scale HTML
    scale_html = '''
    <div class="risk-bar" style="display: flex; gap: 12px; margin: 12px 0 20px;">
        <div style="background-color: #15803d; color: white; padding: 8px 16px; border-radius: 8px; font-weight: bold;">1 – Fit</div>
        <div style="background-color: #3b82f6; color: white; padding: 8px 16px; border-radius: 8px; font-weight: bold;">2 – Can Improve</div>
        <div style="background-color: #facc15; color: black; padding: 8px 16px; border-radius: 8px; font-weight: bold;">3 – Start Improving</div>
        <div style="background-color: #f97316; color: white; padding: 8px 16px; border-radius: 8px; font-weight: bold;">4 – Consult a Professional</div>
        <div style="background-color: #ef4444; color: white; padding: 8px 16px; border-radius: 8px; font-weight: bold;">5 – Strictly Consult</div>
    </div>
    '''

    # 🧠 Step 8: Subheading label based on rating
    rating_labels = {
        "1": "Fit",
        "2": "Can Improve",
        "3": "Start Improving",
        "4": "Consult a Professional",
        "5": "Strictly Consult a Professional"
    }

    subheading_html = ""
    if rating:
        subheading_html = f"<h4 style='color:#f8fafc; font-weight: bold; margin-top: 10px;'>{rating_labels.get(rating, '')}</h4>"
        if explanation:
            subheading_html += f"<p style='margin-top: 6px;'>{explanation}</p>"

    # 💡 Step 9: Inject scale + subheading + explanation
    text = re.sub(
        r"(5\.\s+📊 Lifestyle Quality Rating\s*\(Scale 1–5\):)",
        r"<h3 style='color: #22c55e; font-weight: bold;'>\1</h3>" + scale_html + subheading_html,
        text,
        flags=re.IGNORECASE,
    )

    # Final spacing
    text = text.replace("\n\n", "<br><br>").replace("\n", "<br>")
    return text




# Route 1: Lifestyle Suggestion
@app.route("/generate_suggestion", methods=["POST"])
def generate_lifestyle_suggestion():
    try:
        data = request.get_json()
        print("📅 Lifestyle Data:", data)

        activity_list = data.get('activityType') or []
        activity_list = [str(item) for item in activity_list if item]
        activity_str = ', '.join(activity_list)

        user_prompt = f"""
You are a professional health advisor AI.

Based on the following user lifestyle information, generate a personalized, structured analysis. Respond in 5 clearly separated sections.

User Details:
- Full Name: {data.get('fullName', 'User')}
- Age: {data.get('age')}
- Gender: {data.get('gender')}
- Height: {data.get('height')} cm
- Weight: {data.get('weight')} kg

Sleep Info:
- Duration: {data.get('sleepDuration')} hours
- Timing: {data.get('sleepTiming')}
- Quality: {data.get('sleepQuality')}

Diet & Nutrition:
- Meals/day: {data.get('mealsPerDay')}
- Snacking: {data.get('snacking')}
- Water Intake: {data.get('waterIntake')} liters
- Junk Food: {data.get('junkFood')}
- Fruits/Vegetables per day: {data.get('fruitVegServings')}

Physical Activity:
- Frequency: {data.get('exerciseFrequency')}
- Duration: {data.get('exerciseDuration')} mins
- Activity Type(s): {activity_str}
- Other Activity: {data.get('otherActivity')}

Mental Wellness:
- Stress Level: {data.get('stress')}
- Screen Time: {data.get('screenTime')} hrs
- Work-Life Balance: {data.get('workLife')}

Work & Lifestyle:
- Job Type: {data.get('jobType')}
- Work Hours: {data.get('workHours')}
- Commute Time: {data.get('commuteTime')} mins

Health Deficiency Check:
- Sickness Frequency: {data.get('sickFrequency')} times/year
- Hair Fall: {data.get('hairFall')}
- Disease History: {data.get('diseaseDetails')}

Output format:

1. 👋 Greeting:
"Hi {data.get('fullName', 'User')}, based on your input, here are your personalized health insights:"

2. ✅ Positives:
- [List 2–3 positive habits and for each positive also state how it will help in future ]

3. ⚠ Areas for Improvement:
- [List lifestyle areas that may be risky and why]

4. 🧬 Potential Health Risks (Estimated Percentages):
- [Risk Name]: [Risk %] – [Short explanation]

5. 📊 Lifestyle Quality Rating (Scale 1–5):
[Rating] + Short explanation
"""
        response = model.generate_content(user_prompt)
        raw_reply = response.text.strip()
        print("✅ Gemini Lifestyle Suggestion:", raw_reply)

        formatted = format_response_to_html(raw_reply)
        return jsonify({"suggestion": formatted})

    except Exception as e:
        print("❌ Lifestyle Error:")
        traceback.print_exc()
        return jsonify({"error": str(e)}), 500

# Route 2: Symptom Diagnostic
@app.route("/analyze_symptoms", methods=["POST"])
def analyze_symptoms():
    try:
        data = request.get_json()
        print("📅 Symptom Data:", data)

        symptoms = data.get("symptoms") or []
        symptom_str = ', '.join(symptoms)

        prompt = f"""
You are an experienced AI medical assistant.

A user has submitted the following symptom and health details. Generate a concise diagnostic analysis based on the input.

User Input:
- Full Name: {data.get("fullName", "User")}
- Age: {data.get("age")}
- Gender: {data.get("gender")}

🧠 Symptoms:
- Symptoms: {symptom_str}
- Duration: {data.get("duration")}
- Body Temperature: {data.get("temperature")} °C
- Heart Rate: {data.get("heartRate")} bpm
- Blood Pressure: {data.get("bloodPressure")}

🍽 Diet:
- Diet Details: {data.get("dietDetails")}
- Ate Out: {data.get("ateOut")}
- Junk Food Level: {data.get("junkLevel")}
- Water Intake: {data.get("waterIntake")} L

💤 Sleep:
- Sleep Hours: {data.get("sleepHours")}
- Feel Rested: {data.get("feelRested")}
- Sleep Change: {data.get("sleepChange")}

🏃 Activity & Mood:
- Exercised Recently: {data.get("exercisedRecently")}
- Screen Time: {data.get("screenTime")}
- Recent Mood: {data.get("recentMood")}
- Stress Increased: {data.get("stressIncreased")}

🧬 Medical Background:
- Existing Conditions: {data.get("existingConditions")}
- Medications: {data.get("medications")}
- Allergies: {data.get("allergies")}
- Recent Travel: {data.get("recentTravel")}
- Recent Illness: {data.get("recentIllness")}

🧪 Habits:
- Drinking: {data.get("drinking")}
- Smoking: {data.get("smoking")}
- Tobacco: {data.get("tobacco")}
- Drugs: {data.get("drugs")}

📋 Output format:

1. 👋 Greeting:
"Hi {data.get('fullName', 'User')}, based on your input, here is your personalized diagnosis:"

2. 🧐 Diagnosis:
[List 3–4 potential causes based on diet, sleep, activity, medical background, habits.]

3. ⚠ Future Risk:
[List 3–4 risks the user might face if not treated based on current symptoms.]

4. 🤔 Should you consult a professional:
[State if consultation is needed and suggest doctor specialization.]

5. ⚕ Simple Home Preventions:
[List remedies or state not curable at home if serious.]
"""

        response = model.generate_content(prompt)
        reply = response.text.strip()

        # Remove disclaimer and leading hyphens
        cleaned = reply.split("Disclaimer:")[0].strip()
        cleaned = re.sub(r"(?m)^\s*-\s*", "", cleaned)

        formatted = format_response_to_html(cleaned)
        print("✅ Gemini Symptom Diagnosis:", formatted)

        return jsonify({"suggestion": formatted})

    except Exception as e:
        print("❌ Symptom Error:")
        traceback.print_exc()
        return jsonify({"error": str(e)}), 500
    
    
@app.route("/", methods=["GET"])
def health_check():
 return "✅ Flask backend is running", 200
     
if __name__ == "__main__":
    print("🚀 Combined Gemini Flask server running at http://localhost:5000")
    app.run(debug=True, port=5000)
