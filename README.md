# 🇮🇳 ASOC Mock Test App by VU3NZT

This is a web-based mock test application designed to help aspiring amateur radio operators in India prepare for the **Amateur Station Operator's Certificate (ASOC)** examination. Built with **Streamlit**, this app offers a user-friendly interface for practicing questions from both Section A (Radio Theory) and Section B (Radio Regulations).

-----

### ✨ Features

  * **Two Exam Grades:** Select between "Restricted" and "General" grades, which dynamically adjust the number of questions.
  * **Randomized Questions:** Each time you run the app, a new set of questions is randomly selected from a larger pool.
  * **Intuitive UI:** Easily select your answers using radio buttons for each question.
  * **Instant Results:** Get immediate feedback on your performance after submitting the test, including a breakdown of correct and incorrect answers.
  * **Custom Progress Bars:** Visualize your progress in each section and your overall score with custom-designed progress bars.
  * **"Cheat Mode" for Learning:** A special button allows you to instantly fill in all the correct answers, making it a great study tool for reviewing the material.

-----

### 🙏 Acknowledgements

This project and my journey into amateur radio would not be possible without the guidance and support from the following individuals and organization:

  * **GIAR - Gujarat Institute of Amateur Radio (www.giar.org):** For fostering a community of learners and for providing the resources to pursue my passion for HAM radio.
  * **VU2JGI Dr. Jagdish Pandya & VU2CPV Pravin Valera:** My sincere thanks to my mentors for their invaluable guidance and encouragement throughout my HAM radio training.

-----

### 🚀 How to Run the App

This project is a simple Streamlit application. To run it locally, follow these steps.

#### Prerequisites

Make sure you have Python installed on your system.
You will also need `sectionA_1000.xlsx` and `sectionB_1000.xlsx` files in the same directory as the app to run it.

#### 1\. Clone the Repository

First, clone this repository to your local machine using git:

```bash
git clone https://github.com/ruchirguitar/ASOC-Test-App-by-VU3NZT.git
cd ASOC-Test-App-by-VU3NZT
```

#### 2\. Install Dependencies

The project uses `streamlit` and `pandas`. You can install them with pip:

```bash
pip install -r requirements.txt
# (or)
pip install streamlit pandas
```

#### 3\. Run the App

Once the dependencies are installed, you can start the application with a single command:

```bash
streamlit run app.py
```

This will open a new tab in your web browser with the ASOC Mock Test app.

-----

### 💡 My First GitHub & Python Project

This project is a major milestone for me\! It represents my first attempt at building a functional Python application and sharing it on GitHub. I've learned a lot about:

  * **Python:** Working with data structures, functions, and file handling.
  * **Streamlit:** Building interactive web applications with a simple and elegant framework.
  * **Pandas:** Efficiently reading and manipulating data from Excel files.
  * **GitHub:** Version control, creating a repository, and writing a good README.

A big thank you to the help of a large language model, which was an invaluable assistant throughout the coding process, helping me debug issues and improve the code. This project is a testament to what can be achieved with the right tools and a passion for learning.

-----

### 🤝 Contributing & Future Improvements

This project is a work in progress and there's always room for improvement\! If you have any ideas, suggestions, or bug reports, feel free to open an issue or submit a pull request.

Here are some ideas for future development:

  * Add a timer for the mock test.
  * Implement a dark mode toggle.
  * Allow users to save their progress or results.
  * Enhance the UI with more custom CSS.

I hope this app is useful for anyone preparing for the ASOC exam\!
