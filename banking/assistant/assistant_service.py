import os
import json
import requests
from typing import Dict, Any
from .query_grounding import ground_query


def format_deterministic_response(intent: str, facts: Dict[str, Any], user_query: str) -> str:
    curr = facts.get('currency', 'INR')
    sym = '₹' if curr == 'INR' else ('$' if curr == 'USD' else f"{curr} ")

    if intent == 'SPEND_THIS_MONTH':
        total = facts.get('total_spent', 0.0)
        timeframe = facts.get('timeframe', 'This Month')
        count = facts.get('transaction_count', 0)
        top = facts.get('top_categories_this_month', [])

        text = f"### 📊 Spending Summary for {timeframe}\n\n"
        text += f"- **Total Expenses:** **{sym}{total:,.2f}**\n"
        text += f"- **Number of Transactions:** {count}\n\n"
        if top:
            text += "#### Top Spending Categories:\n"
            for t in top:
                text += f"- **{t['category']}:** {sym}{t['amount']:,.2f}\n"
        else:
            text += "_No categorized debit transactions found for this period._\n"
        return text

    elif intent == 'HIGHEST_CATEGORY':
        cat = facts.get('highest_category', 'None')
        amt = facts.get('highest_category_amount', 0.0)
        pct = facts.get('percentage_of_all_expenses', 0.0)
        count = facts.get('highest_category_count', 0)
        all_cats = facts.get('all_categories', [])

        text = f"### 🏆 Highest Expenditure Category\n\n"
        text += f"Your highest expenditure category is **{cat}** with total spending of **{sym}{amt:,.2f}** ({pct}% of your total expenses across {count} transactions).\n\n"
        if all_cats:
            text += "#### Category Breakdown:\n"
            text += "| Category | Total Spent |\n| :--- | :--- |\n"
            for c in all_cats:
                text += f"| **{c['category']}** | {sym}{c['amount']:,.2f} |\n"
        return text

    elif intent == 'TOP_EXPENSES':
        top = facts.get('top_transactions', [])
        text = "### 💳 Top 5 Expenses\n\n"
        if not top:
            text += "No expense transactions recorded yet."
            return text

        text += "| Date | Description | Category | Amount | Account |\n"
        text += "| :--- | :--- | :--- | :--- | :--- |\n"
        for t in top:
            text += f"| {t['date']} | {t['description']} | **{t['category']}** | **{sym}{t['amount']:,.2f}** | {t['account']} |\n"
        return text

    elif intent == 'COMPARE_MONTHS':
        curr_lbl = facts.get('current_month_label')
        prev_lbl = facts.get('previous_month_label')
        curr_exp = facts.get('current_month_expenses', 0.0)
        prev_exp = facts.get('previous_month_expenses', 0.0)
        diff = facts.get('difference_amount', 0.0)
        pct = facts.get('percentage_change', 0.0)
        direction = facts.get('direction', 'flat')

        text = f"### ⚖️ Month-over-Month Expense Comparison\n\n"
        text += f"Comparing **{curr_lbl}** with **{prev_lbl}**:\n\n"
        text += f"- **{curr_lbl} Expenses:** {sym}{curr_exp:,.2f}\n"
        text += f"- **{prev_lbl} Expenses:** {sym}{prev_exp:,.2f}\n"
        if direction == 'increased':
            text += f"- **Trend:** 🔺 Spending increased by **{sym}{diff:,.2f}** (+{pct}%)\n\n"
        elif direction == 'decreased':
            text += f"- **Trend:** 🟢 Spending decreased by **{sym}{diff:,.2f}** ({pct}% savings improvement)\n\n"
        else:
            text += f"- **Trend:** ➖ Spending remained unchanged.\n\n"
        return text

    elif intent == 'SALARY_CREDITED':
        total = facts.get('total_salary_credited', 0.0)
        count = facts.get('total_salary_count', 0)
        recent = facts.get('recent_salary_transactions', [])

        text = f"### 💼 Salary & Payroll Credits\n\n"
        text += f"- **Total Recorded Salary:** **{sym}{total:,.2f}** ({count} deposits)\n\n"
        if recent:
            text += "#### Recent Payroll Deposits:\n"
            text += "| Date | Description | Account | Amount |\n| :--- | :--- | :--- | :--- |\n"
            for r in recent:
                text += f"| {r['date']} | {r['description']} | {r['account']} | **{sym}{r['amount']:,.2f}** |\n"
        return text

    elif intent == 'UNUSUAL_TRANSACTIONS':
        unusual = facts.get('unusual_transactions', [])
        text = "### ⚠️ Unusual Spending & Anomaly Detection\n\n"
        if not unusual:
            text += "✅ Great news! No anomalous or unusually high spending detected in your transaction history."
            return text

        text += "The following transactions stand out as significantly higher than your typical average spend:\n\n"
        text += "| Date | Description | Category | Amount | Account |\n| :--- | :--- | :--- | :--- | :--- |\n"
        for u in unusual:
            text += f"| {u['date']} | {u['description']} | **{u['category']}** | **{sym}{u['amount']:,.2f}** | {u['account']} |\n"
        return text

    elif intent == 'SAVINGS_THREE_MONTHS':
        timeframe = facts.get('timeframe')
        income = facts.get('total_income', 0.0)
        exp = facts.get('total_expenses', 0.0)
        net = facts.get('net_savings', 0.0)
        rate = facts.get('savings_rate', 0.0)

        text = f"### 💰 Savings Report ({timeframe})\n\n"
        text += f"- **Total Income:** {sym}{income:,.2f}\n"
        text += f"- **Total Expenses:** {sym}{exp:,.2f}\n"
        text += f"- **Net Savings:** **{sym}{net:,.2f}**\n"
        text += f"- **Savings Rate:** **{rate}%**\n\n"
        if rate >= 20:
            text += "🌟 Your savings rate is healthy (above recommended 20% benchmark)!"
        elif rate > 0:
            text += "💡 You have positive savings. Aiming for 20% savings rate can help build emergency reserves."
        else:
            text += "⚠️ Expenses exceeded income during this period. Review discretionary categories like Food and Shopping."
        return text

    elif intent == 'ACCOUNT_BALANCE':
        total = facts.get('total_balance', 0.0)
        accounts = facts.get('accounts', [])

        text = f"### 🏦 Account Balances\n\n"
        text += f"- **Total Net Balance:** **{sym}{total:,.2f}**\n\n"
        if accounts:
            text += "| Account | Bank | Number | Balance |\n| :--- | :--- | :--- | :--- |\n"
            for a in accounts:
                text += f"| **{a['name']}** | {a['bank']} | {a['masked_number']} | **{sym}{a['balance']:,.2f}** |\n"
        return text

    elif intent.startswith('CATEGORY_'):
        cat = facts.get('category', 'Category')
        total = facts.get('total_spent', 0.0)
        count = facts.get('count', 0)
        recent = facts.get('recent_transactions', [])

        text = f"### 🏷️ Spending in {cat}\n\n"
        text += f"- **Total Spent:** **{sym}{total:,.2f}** across {count} transactions\n\n"
        if recent:
            text += "#### Recent Transactions:\n"
            for r in recent:
                text += f"- {r['date']} — **{sym}{r['amount']:,.2f}** ({r['description']})\n"
        return text

    else:
        # General Summary
        bal = facts.get('total_balance', 0.0)
        inc = facts.get('total_income', 0.0)
        exp = facts.get('total_expenses', 0.0)
        net = facts.get('net_savings', 0.0)
        count = facts.get('transaction_count', 0)
        top = facts.get('top_categories', [])

        text = "### 📈 BankSense AI Financial Activity Overview\n\n"
        text += f"- **Current Total Balance:** **{sym}{bal:,.2f}**\n"
        text += f"- **Total Income Recorded:** {sym}{inc:,.2f}\n"
        text += f"- **Total Expenses Recorded:** {sym}{exp:,.2f}\n"
        text += f"- **Net Savings:** **{sym}{net:,.2f}**\n"
        text += f"- **Total Transactions:** {count}\n\n"
        if top:
            text += "#### Top Expense Categories:\n"
            for t in top:
                text += f"- **{t['category']}:** {sym}{t['amount']:,.2f}\n"
        return text


def ask_ai_assistant(user, query: str) -> Dict[str, Any]:
    # 1. Deterministic grounding
    facts = ground_query(user, query)
    intent = facts.get('intent', 'GENERAL_SUMMARY')

    deterministic_answer = format_deterministic_response(intent, facts, query)

    # 2. Check if Gemini or OpenAI API key is configured
    gemini_key = os.getenv('GEMINI_API_KEY')
    openai_key = os.getenv('OPENAI_API_KEY')

    if gemini_key:
        try:
            url = f"https://generativelanguage.googleapis.com/v1beta/models/gemini-1.5-flash:generateContent?key={gemini_key}"
            payload = {
                "contents": [
                    {
                        "role": "user",
                        "parts": [
                            {
                                "text": (
                                    "You are BankSense AI, an expert banking and financial intelligence assistant.\n"
                                    "You MUST ground your response strictly on the verified mathematical data below.\n"
                                    "RULES:\n"
                                    "1. NEVER invent, hallucinate, or alter financial numbers.\n"
                                    "2. Use markdown formatting with bullet points and bold amounts.\n"
                                    "3. Address the user's question directly with concise, empathetic financial advice.\n\n"
                                    f"User Question: '{query}'\n"
                                    f"Verified Grounded Facts:\n{json.dumps(facts, indent=2)}\n"
                                )
                            }
                        ]
                    }
                ],
                "generationConfig": {
                    "temperature": 0.2,
                    "maxOutputTokens": 600,
                }
            }
            resp = requests.post(url, json=payload, timeout=8)
            if resp.status_code == 200:
                ai_text = resp.json()['candidates'][0]['content']['parts'][0]['text']
                return {
                    'response': ai_text,
                    'intent': intent,
                    'grounded_facts': facts,
                    'engine': 'gemini-1.5-flash',
                }
        except Exception:
            pass  # Fall back gracefully to deterministic answer

    elif openai_key:
        try:
            headers = {
                "Authorization": f"Bearer {openai_key}",
                "Content-Type": "application/json"
            }
            payload = {
                "model": "gpt-4o-mini",
                "messages": [
                    {
                        "role": "system",
                        "content": "You are BankSense AI financial assistant. Answer the user query using only the provided verified financial metrics. Do not fabricate numbers."
                    },
                    {
                        "role": "user",
                        "content": f"User Query: {query}\nVerified Data: {json.dumps(facts)}"
                    }
                ],
                "temperature": 0.2,
                "max_tokens": 500
            }
            resp = requests.post("https://api.openai.com/v1/chat/completions", headers=headers, json=payload, timeout=8)
            if resp.status_code == 200:
                ai_text = resp.json()['choices'][0]['message']['content']
                return {
                    'response': ai_text,
                    'intent': intent,
                    'grounded_facts': facts,
                    'engine': 'openai-gpt-4o-mini',
                }
        except Exception:
            pass

    # Deterministic high-precision fallback
    return {
        'response': deterministic_answer,
        'intent': intent,
        'grounded_facts': facts,
        'engine': 'deterministic-grounded-engine',
    }

