import google.generativeai as genai
from flask import Flask, redirect, url_for, render_template, request
import re


genai.configure(api_key="ENTER GEMINI API KEY HERE")



model = genai.GenerativeModel("gemini-pro")

safe = [
    {
        "category": "HARM_CATEGORY_HARASSMENT",
        "threshold": "BLOCK_NONE",
    },
    {
        "category": "HARM_CATEGORY_HATE_SPEECH",
        "threshold": "BLOCK_NONE",
    },
    {
        "category": "HARM_CATEGORY_SEXUALLY_EXPLICIT",
        "threshold": "BLOCK_NONE",
    },
    {
        "category": "HARM_CATEGORY_DANGEROUS_CONTENT",
        "threshold": "BLOCK_NONE",
    },
]

app = Flask(__name__)


# removing * and #
def remove(text):
    remove = re.compile(r"(\*|#)")
    clean_text = re.sub(remove, "", text)
    return clean_text


# subtopics
def subtopic(nos, chapter, topic):
    sub = model.generate_content(f"Generate only {nos} subtopics for chapter named {chapter} for a book that teaches {topic} ")
    return sub.text


def gen_intro(topic, i):
    try:
        intro = model.generate_content(f"Write 2000 words explaining in detail {i} for a book that teaches {topic}, start the answer with the topic's name written in bold.")
        return intro.text
    except ValueError:
        intro = model.generate_content(f"Write 2000 words explaining in detail {i} for a book that teaches {topic}, start the answer with the topic's name written in bold.")
        return intro.text


def gen_ques(intro, depth):
    q = model.generate_content(f"Generate {depth} questions that a high school student will ask after reading this paragraph {intro}, avoiding starting the output by writing Questions.")
    return q.text


def gen_ans(ques):
    try:
        ans = model.generate_content(f"Explain in detail {ques}. Provide examples or analogies to help clarify complex concepts and ensure a comprehensive understanding. Start the answer with the name of the topic that the answer should cover.")
        a = remove(ans.text)
        return a
    except ValueError:
        ans = model.generate_content(f"Explain in detail {ques}. Provide examples or analogies to help clarify complex concepts and ensure a comprehensive understanding. Start the answer with the name of the topic that the answer should cover.")
        a = remove(ans.text)
        return a


def gen_wwwl(chapter):
    try:
        wwwl = model.generate_content(f"Generate a detailed paragraph about what I will learn from these chapters and subtopics {chapter}, start the paragraph with the heading 'What We Will Learn'.")
        a = remove(wwwl.text)
        return a
    except ValueError:
        wwwl = model.generate_content(f"Generate a detailed paragraph about what I will learn from these chapters and subtopics {chapter}, start the paragraph with the heading 'What We Will Learn'.")
        a = remove(wwwl.text)
        return a


def gen_ff(chapter, topic):
    try:
        fact = model.generate_content(f"Write 3-5 fun facts related to this chapter {chapter} in the context of {topic}")
        a = remove(fact.text)
        return a
    except ValueError:
        fact = model.generate_content(f"Write 3-5 fun facts related to this chapter {chapter} in the context of {topic}")
        a = remove(fact.text)
        return a


def gen_quiz(i):
    quiz = model.generate_content(f"Generate 10 to 20 quizzes for this chapter and subtopics {i}")
    a = remove(quiz.text)
    return a


# main web page:
@app.route("/", methods=['GET', 'POST'])
def home():
    return render_template("index.html")


@app.route("/book", methods=['GET', 'POST'])
def book():
    if request.method == "POST":
        # taking input from the user 
        topic = request.form["topic"]
        chap_count = request.form["chap"]
        nos = request.form["nos"]
        depth = request.form["depth"]

        # generating book's name 
        name = model.generate_content(f"What should be the name of a book that teaches {topic}? Give only one name.")

        # generating chapters
        chapters = model.generate_content(f"Write only {chap_count} chapters that a book named {name.text.strip()} will teach. Write only the chapter names and nothing else.")

        chapter_removed = remove(chapters.text)

        chap_list = chapter_removed.split("\n")

        # generating subtopics
        sub_t = [subtopic(nos, chapter, topic) for chapter in chap_list]

        # dividing sub_t list into multiple lists
        subtopic_list = []
        for i in sub_t:
            a = remove(i)
            sub = a.split("\n")
            subtopic_list.append(sub)

        # explaining subtopics
        intro = [gen_intro(topic, i) for subt in subtopic_list for i in subt]

        intro_temp = []
        for i in range(0, len(intro), int(nos)):
            temp = []
            temp = intro[i:i + int(nos)]
            intro_temp.append(temp)

        # dividing subtopic list
        intro_list = []
        for i in intro_temp:
            temp = []
            for j in i:
                r = remove(j)
                temp.append(r)
            intro_list.append(temp)

        # generating questions 
        ques = [gen_ques(i, depth) for j in intro_list for i in j]

        # dividing question list
        que_list = [i.split("\n") for i in ques]

        main_que_list = []
        for i in range(0, len(que_list), int(nos)):
            que_temp = []
            que_temp = que_list[i:i + int(nos)]
            main_que_list.append(que_temp)

        # generating answers
        ans = [gen_ans(k) for i in main_que_list for j in i for k in j]

        # dividing answer list
        ans_list = []
        for i in range(0, len(ans), int(depth)):
            ans_temp = ans[i:i + int(depth)]
            ans_list.append(ans_temp)

        # wwwl
        linked_list = [(chap_list[i], subtopic_list[i]) for i in range(min(len(chap_list), len(subtopic_list)))]
        wwwl = [gen_wwwl(chap) for chap, _ in linked_list]

        # fun facts
        fun_facts = [gen_ff(i, topic) for i in chap_list]

        # generating quizzes
        quiz = [gen_quiz(chap) for chap, _ in linked_list]

        return render_template("book.html", name=name.text.strip(), chap_list=chap_list, subtopic_list=subtopic_list,
                               intro=intro, intro_list=intro_list, que_list=main_que_list, ans_list=ans_list, wwwl=wwwl,
                               fun_facts=fun_facts, quiz=quiz)
    else:
        return render_template("index.html")


if __name__ == "__main__":
    app.run(debug=True)
