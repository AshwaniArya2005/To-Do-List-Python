import streamlit as st
from datetime import date
import firebase_admin
from firebase_admin import credentials, firestore
import time
import pandas as pd

# Initialize Firebase Admin
if not firebase_admin._apps:
    cred = credentials.Certificate(
        'taskmanagement-5a659-firebase-adminsdk-csgh1-8223df55ed.json')  # Update with the correct path
    firebase_admin.initialize_app(cred, {
        'databaseURL': 'https://taskmanagement-5a659-default-rtdb.asia-southeast1.firebasedatabase.app/'} )
db = firestore.client()

# Home Page (Intro Page)
def home_page():
    st.markdown(
        """
        <style>
        .stApp {
            background: url("https://img.freepik.com/free-photo/nice-business-desk-black-background_24972-1177.jpg?t=st=1734365943~exp=1734369543~hmac=ca03b097d60af0173e5e35fac549b38e32b211810fb35640d6c363d32c2aa44a&w=1380") no-repeat center center fixed; 
            background-size: cover;
        }
        .centered-container {
            display: flex;
            justify-content: center;
            align-items: center;
            height: 100vh;
            flex-direction: column;
        }
        </style>
        """,
        unsafe_allow_html=True
    )

    st.markdown("<h1 style='color: white; text-align: center;'>Welcome to the Task Management App!</h1>", unsafe_allow_html=True)
    st.markdown("<p style='color: white; text-align: center; font-size: 18px;'>Easily manage your tasks and stay productive.</p>", unsafe_allow_html=True)
    st.markdown("<p style='color: white; text-align: center;'>Click on 'To-do List' to start managing your tasks.</p>", unsafe_allow_html=True)


# About Us Page
def about_us_page():
    st.markdown(
        """
        <style>
        .stApp {
            background: url("https://img.freepik.com/free-photo/top-view-desk-concept-with-laptop_23-2148236828.jpg?t=st=1734357080~exp=1734360680~hmac=945db2e73be365f5fbd61b4d8f3660778b9d37782162f0b38eb240727922686d&w=1380") no-repeat center center fixed; 
            background-size: cover;
        }
        </style>
        """,
        unsafe_allow_html=True
    )
    st.markdown("<h1 style='font-size: 34px; color: red; font-size: 40px; text-align: left;'>About Us</h1>", unsafe_allow_html=True)
    st.markdown("<p style='font-size: 26px; color: black; text-align: left;'>Welcome to Task Management, a dynamic web application designed to help individuals manage their tasks efficiently. Whether you're a student, professional, or someone looking to organize your day-to-day activities, this platform offers a simple and intuitive interface for managing tasks with ease.</p>", unsafe_allow_html=True)
    st.markdown(" ")
    st.markdown("<p style='font-size: 26px; color: black; text-align: left;'>Our goal is to make task management as seamless as possible, with features like task prioritization, deadlines, and customizable categories. Sign up today and take control of your tasks!</p>", unsafe_allow_html=True)

def task_management_page():
    st.title("To-Do List")

    st.markdown(
        """
        <style>
        .stApp {
            background: url("https://img.freepik.com/free-photo/composition-laptop-compass-engineering_23-2148169502.jpg?t=st=1734366027~exp=1734369627~hmac=e3185fbafdd86a9ba58430f2c7716a7db89df27e778e076850dd30ea9306f3db&w=1380") no-repeat center center fixed; 
            background-size: cover;
        }
        .curved-box {
            background-color: rgba(255, 255, 255, 0.8);
            border-radius: 25px;
            padding: 20px;
            margin: 10px;
            box-shadow: 0 4px 8px rgba(0, 0, 0, 0.2);
            width: 80%;
            text-align: center;
        }
        .delete-button {
            background-color: red;
            color: white;
            padding: 10px;
            font-size: 14px;
            border-radius: 5px;
            border: none;
            cursor: pointer;
        }
        .delete-button:hover {
            background-color: darkred;
        }
        </style>
        """,
        unsafe_allow_html=True
    )

    st.markdown(
        """
        <div class='curved-box'>
            <h2 style='color: "Dark blue"; font-family: "Open Sans", sans-serif; font-size: 35px; text-shadow: 2px 2px 4px rgba(0, 0, 0, 0.5);'>
                Manage Your Tasks
            </h2>
        </div>
        """,
        unsafe_allow_html=True
    )

    tasks_ref = db.collection('tasks').document('default_user').collection('user_tasks')
    tasks = tasks_ref.stream()
    tasks_list = []

    for task in tasks:
        task_data = task.to_dict()
        task_data['task_id'] = task.id  # Add the Firestore document ID as task_id
        tasks_list.append(task_data)

    # Convert tasks to a DataFrame for displaying in table format
    df = pd.DataFrame(tasks_list)

    # Display Add New Task Form
    task_name = st.text_input("Task Name", key="task_name_input")
    task_deadline_date = st.date_input("Task Deadline Date", min_value=date.today(), key="task_deadline_date_input")
    task_priority = st.selectbox("Priority", ["High", "Medium", "Low"], key="task_priority_input")
    task_category = st.selectbox("Category", ["Started", "Processing", "Ended"], key="task_category_input")

    # Check if the task name already exists
    existing_task_names = [task['Task Name'] for task in tasks_list]

    if st.button("Add Task", key="add_task_button"):
        if not task_name.strip():  # Check for empty task name
            st.error("Task name cannot be empty!")
        elif task_name.strip() in existing_task_names:  # Check for duplicate task name
            st.error(f"Task with name '{task_name.strip()}' already exists!")
        else:
            new_task = {
                "Task Name": task_name.strip(),
                "Task Deadline Date": task_deadline_date.strftime("%Y-%m-%d"),  # Convert date to string
                "Priority": task_priority,
                "Category": task_category
            }

            tasks_ref.add(new_task)
            st.success("Task added successfully.")

    # Display table and delete buttons at the bottom
    if not df.empty:
        st.dataframe(df[['Task Name', 'Task Deadline Date', 'Priority', 'Category']])  # Display the table with relevant columns
        for index, row in df.iterrows():
            # Create a delete button for each task, using its name as the key
            delete_button = st.button(f"Delete Task {row['Task Name']}", key=f"delete_{row['Task Name']}")

            # If the delete button is clicked, pass the task name to the delete_task function
            if delete_button:
                delete_task(row['Task Name'])  # Pass task name to delete_task function
    else:
        st.warning("No tasks found.")


def delete_task(task_id):
    try:
        tasks_ref = db.collection('tasks').document('default_user').collection('user_tasks')
        task_to_delete = tasks_ref.document(task_id)
        task_to_delete.delete()  # Delete the task from Firestore
        st.success(f"Task with ID '{task_id}' deleted successfully!")
    except Exception as e:
        st.error(f"Error deleting task: {e}")


# Initialize session state
if 'page' not in st.session_state:
    st.session_state.page = "home"  # Default page is Home
if 'refresh_tasks' not in st.session_state:
    st.session_state.refresh_tasks = False


# Sidebar Navigation
st.sidebar.title("Navigation")
if st.sidebar.button("Home", key="nav_home"):
    st.session_state.page = 'home'
if st.sidebar.button("To-do List", key="nav_todolist"):
    st.session_state.page = 'task_management'
if st.sidebar.button("About Us", key="nav_about"):
    st.session_state.page = 'about'


# Main Page Rendering
if st.session_state.page == "home":
    home_page()
elif st.session_state.page == "task_management":
    task_management_page()
elif st.session_state.page == "about":
    about_us_page()
