import requests
from bs4 import BeautifulSoup
from lxml import etree
import json

# URL to scrape
url = "https://www.arizona.edu/admissions/faq"

# Fetch the webpage
headers = {"User-Agent": "Mozilla/5.0"}  # Helps avoid blocking
response = requests.get(url, headers=headers)

if response.status_code == 200:
    # Parse with BeautifulSoup using lxml
    soup = BeautifulSoup(response.content, "lxml")

    # Convert to an lxml element tree
    dom = etree.HTML(str(soup))

    # Extract FAQ questions and answers using XPath
    # faq_data = []
    # questions = dom.xpath("//*[contains(@class, 'Faqs__FAQTitle')]/text()")
    # answers = dom.xpath("//*[contains(@class, 'Faqs__FAQContentWrapper')]//text()")
    # import pdb;pdb.set_trace()

    # # Combine questions and answers into a list of dictionaries
    # for question, answer in zip(questions, answers):
    #     faq_data.append({
    #         "question": question.strip(),
    #         "answer": answer.strip()
    #     })

    faq_data = []
    questions = dom.xpath("//*[contains(@class, 'Faqs__FAQTitle')]")
    
    for question in questions:
        # Get the question text
        question_text = question.xpath("string()").strip()

        # Find the corresponding answer for each question by navigating the DOM
        answer = question.xpath("../following-sibling::div[contains(@class, 'Faqs__FAQContentWrapper')]//p//text()")

        # Combine all parts of the answer into a single string
        combined_answer = " ".join([a.strip() for a in answer if a.strip()])

        # Append the question and its corresponding answer to the list
        faq_data.append({
            "question": question_text,
            "answer": combined_answer
        })

    # Save to JSON
    with open("faq_data.json", "w", encoding="utf-8") as file:
        json.dump(faq_data, file, ensure_ascii=False, indent=4)

    print("Scraped FAQ Data:", faq_data)
    print("Data saved to 'faq_data.json' ✅")

else:
    print("Failed to fetch page. Status Code:", response.status_code)
