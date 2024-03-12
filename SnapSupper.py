import streamlit as st
import boto3
from botocore.exceptions import NoCredentialsError
import uuid
from PIL import Image
import io
import openai
from openai import OpenAI


# Function to set a background image and black banner
def set_background():
    st.markdown(
        f"""
        <style>
        .stApp {{
            background-image: url("https://raw.githubusercontent.com/alikassi/kitchen_image.jpg/main/kitchen_image.jpg");
            background-size: cover;
        }}
        .stTitleBanner {{
            background-color: rgba(0, 0, 0, 0.8);  /* Semi-transparent black banner */
            padding: 40px;  /* Increase padding to accommodate subtext */
            border-radius: 0 0 10px 10px;  /* Add rounded corners to the bottom */
        }}
        .stTitleBox {{
            background-color: rgba(0, 0, 0, 0.8);  /* Semi-transparent black box */
            padding: 20px;  /* Increase padding */
            border-radius: 10px;  /* Add rounded corners */
            margin-bottom: 20px;  /* Add margin below the box */
            color: white;  /* Set text color to white */
        }}
        .stText {{
            color: white;  /* Set subtext color to white */
            font-size: large;  /* Adjust subtext font size */
        }}
        .review-button {{
            cursor: pointer;
            color: blue;
            background-color: rgba(0, 0, 0, 0.5);  /* Semi-transparent black button */
            padding: 10px 20px;  /* Add padding to the button */
            border-radius: 5px;  /* Add rounded corners */
        }}
        .modal {{
            display: none;
            position: fixed;
            z-index: 1;
            left: 0;
            top: 0;
            width: 100%;
            height: 100%;
            overflow: auto;
            background-color: rgba(0, 0, 0, 0.4);  /* Semi-transparent black overlay */
            padding-top: 60px;
        }}
        .modal-content {{
            background-color: rgba(0, 0, 0, 0.8);  /* Semi-transparent black box */
            margin: 5% auto;
            padding: 20px;
            border: 1px solid #888;
            width: 80%;
            color: white;  /* Set text color to white */
        }}
        .form-text {{
            background-color: rgba(255, 255, 255, 0.1);  /* Semi-transparent white text box */
            color: white;  /* Set text color to white */
        }}
        </style>
        """,
        unsafe_allow_html=True
    )

# Function for Home Page

# Function for Home Page
def display_image_popup(image_filenames, visibility, key):
    # Display the additional images based on the selected main image
    if visibility[key]:
        for img_filename in image_filenames:
            if img_filename.endswith('_r.png') or img_filename.endswith('_NF.jpeg'):
                st.image(img_filename, width=500)  # Adjust width as needed
            elif img_filename.endswith('_ins.png'):
                st.image(img_filename, width=500)  # Adjust width as needed
def home_page():
    # Titles and main images
    titles = ["Vegetarian Recipe", "Gluten-Free Dessert", "Diabetes Friendly"]
    main_images = ["Veg.jpeg", "CC.jpeg", "DM.jpeg"]
    
    # Additional images for each category
    additional_images = {
        "Vegetarian Recipe": ["veg_r.png", "veg_ins.png"],
        "Gluten-Free Dessert": ["GF_r.png", "GF_ins.png"],
        "Diabetes Friendly": ["DM_r.png", "DM_ins.png"]
    }
    nutritional_images = {
        "Vegetarian Recipe": ["veg_NF.jpeg"],
        "Gluten-Free Dessert": ["GF_NF.jpeg"],
        "Diabetes Friendly": ["DM_NF.jpeg"]
    }

    # Define initial visibility states for each additional image
    recipe_visibility = {title: False for title in titles}
    nutritional_visibility = {title: False for title in titles}

    st.markdown("""
    <div class="stTitleBanner">
        <h1 class="stTitle">Meal Master</h1>
        <p class="stText">Welcome to Meal Master! Upload a photo of your fridge on the "MealMaster" page to get started.</p>
    </div>
    """,
    unsafe_allow_html=True
)

    # Inject custom CSS styles for the titles
    st.markdown("""
        <style>
        .image-title {
            font-weight: bold;
            font-size: 18px; /* Adjust font size as needed */
            color: #ffffff; /* White text color */
            background-color: rgba(0,0,0,0.5); /* Semi-transparent black background */
            padding: 5px;
            border-radius: 5px; /* Rounded corners */
            text-align: center; /* Center-align text */
        }
        </style>
    """, unsafe_allow_html=True)

    cols = st.columns(3)
    for col, title, main_img in zip(cols, titles, main_images):
        with col:
            st.markdown(f"<div class='image-title'>{title}</div>", unsafe_allow_html=True)
            st.image(main_img, width=300)  # Display the main image
            button_clicked = False
            if st.button('Recipe', key=f"{title}_recipe"):
                button_clicked = True
                # Toggle recipe visibility when the recipe button is clicked
                recipe_visibility[title] = not recipe_visibility[title]
            if st.button('Nutritional Facts', key=f"{title}_nutrition"):
                button_clicked = True
                # Toggle nutritional visibility when the nutritional button is clicked
                nutritional_visibility[title] = not nutritional_visibility[title]
            # If no button is clicked, display nutritional images by default
            if not button_clicked:
                display_image_popup(nutritional_images[title], nutritional_visibility, title)
            # Display images based on visibility flags
            if recipe_visibility[title]:
                display_image_popup(additional_images[title], recipe_visibility, title)
            elif nutritional_visibility[title]:
                display_image_popup(nutritional_images[title], nutritional_visibility, title)



prompt = "What are ingredients in this fridge? And can you create recipes from it"


def upload_file_to_s3(image_path):
    """
    Uploads a file to an S3 bucket using securely input AWS credentials.

    Args:
        file (object): File to upload
    Returns:
        The URL of the uploaded file
    """
    # S3 object_name, file_name generated randomly
    file_name = str(uuid.uuid4())  # Generate a random UUID.
    object_name = file_name + '.jpg'

    # Create an S3 client with the provided credentials
    s3_client = boto3.client('s3',
                             aws_access_key_id='AKIATCKAOGBZJDNZJPSS',
                             aws_secret_access_key='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')

    try:
        # Upload the file with public-read access
        s3_client.upload_fileobj(image_path, 'recipegeneration', object_name)

        # Construct URL of the uploaded file
        url = f"https://recipegeneration.s3.amazonaws.com/{object_name}"
        return url
    except NoCredentialsError:
        print("Credentials not available")
        return None
    except Exception as e:
        print(e)
        return None
  

# Function to process the image
def process_image(image):
    # Create a bytes buffer for the image
    img_byte_arr = io.BytesIO()
    
    # Save the image to the bytes buffer
    image.save(img_byte_arr, format='JPEG')  # Use the appropriate format (e.g., JPEG, PNG)
    
    # Seek the start of the stream
    img_byte_arr.seek(0)

    image_url = upload_file_to_s3(img_byte_arr)

    return image_url


def recipe_generator():
    st.title("💬 Meal Master")
    st.caption("🚀 A Streamlit chatbot powered by OpenAI LLM")
   
    # Check if 'image_url' is already in the session state to avoid resetting it
    if 'image_url' not in st.session_state:
        st.session_state['image_url'] = None  # Initialize image_url only if it's not already set


    # Sidebar for OpenAI API Key input
    with st.sidebar:
        openai_api_key = "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"
        "[View the source code](https://github.com/streamlit/llm-examples/blob/main/Chatbot.py)"
        "[![Open in GitHub Codespaces](https://github.com/codespaces/badge.svg)](https://codespaces.new/streamlit/llm-examples?quickstart=1)"
        
    # Initialize conversation history in session state
    if 'conversation_history' not in st.session_state:
        st.session_state['conversation_history'] = []

    # Display conversation history
    for message in st.session_state['conversation_history']:
        if message['role'] == "user":
            st.chat_message("user").write(message['content'])
        else:
            st.chat_message("assistant").write(message['content'])

    # Check if an image is already uploaded and stored in session state
    if 'uploaded_image' not in st.session_state:
        # Initialize the session state for the uploaded image
        st.session_state['uploaded_image'] = None
    
    # File uploader for image
    uploaded_image = st.file_uploader("Upload Image (Optional)", type=["jpg", "png", "jpeg"])

    # Text input and send button
    user_input_text = st.text_input("Enter your message", key="user_message", on_change=None)
    send_button = st.button("Send")

    if uploaded_image is not None:
         # Check if the newly uploaded image is different from the one in session state
        if st.session_state['uploaded_image'] != uploaded_image:
            # Update the session state with the new image
            st.session_state['uploaded_image'] = uploaded_image
            
            # Process the uploaded image
            image = Image.open(uploaded_image)
            image_url = process_image(image)  # Your image processing function

            st.session_state['image_url'] = image_url
            st.session_state['conversation_history'].append({"role": "user", "content": image_url})


    # Dietary preferences
    st.header("Dietary Preferences")
    dietary_preferences_options = [
        "Lactose intolerance",
        "Gluten intolerance or sensitivity",
        "Vegetarianism",
        "Veganism",
        "Kosher",
        "Keto",
        "Diabetes",
        "Dairy-free"
    ]
    dietary_preferences_selected = st.multiselect("Select dietary preferences", dietary_preferences_options)

    # Other dietary preferences
    other_dietary_preference = st.checkbox("Other (please specify)", key="other_dietary_preference_checkbox")
    if other_dietary_preference:
        other_dietary_preference_text = st.text_input("Other dietary preferences", key="other_dietary_preference_text")

    # Allergies
    st.header("Allergies")
    allergies_options = [
        "Milk",
        "Eggs",
        "Fish",
        "Crustacean shellfish",
        "Tree nuts",
        "Peanuts",
        "Wheat",
        "Soybeans"
    ]
    allergies_selected = st.multiselect("Select allergies", allergies_options)

    # Other allergies
    other_allergies = st.checkbox("Other (please specify)", key="other_allergies_checkbox")
    if other_allergies:
        other_allergies_text = st.text_input("Other allergies", key="other_allergies_text")

    # Process user input and generate response
    if send_button:
        if not openai_api_key:
            st.info("Please add your OpenAI API key to continue.")
            st.stop()
        
        if user_input_text.strip():  
            st.session_state['conversation_history'].append({"role": "user", "content": user_input_text})
        # if uploaded_image is not None:
        #     st.session_state['conversation_history'].append({"role": "user", "content": image_url})

        client = OpenAI(api_key=openai_api_key)
        
        user_message = user_input_text
        if dietary_preferences_selected:
            user_message += "\n\nDietary Preferences: "
            user_message += ", ".join(dietary_preferences_selected)
            if other_dietary_preference and other_dietary_preference_text:
                user_message += f", {other_dietary_preference_text}"
        
        if allergies_selected:
            user_message += "\n\nAllergies: "
            user_message += ", ".join(allergies_selected)
            if other_allergies and other_allergies_text:
                user_message += f", {other_allergies_text}"
       
        messages = []
        if uploaded_image is not None:
            messages.append({
                "role": "user",
                "content": [
                    {"type": "text", "text": user_message},
                    {"type": "image_url", "image_url": {"url": st.session_state['image_url']}},
                ]
            })
        else:
            messages.append({
                "role": "user",
                "content": [{"type": "text", "text": user_message}]
            })

        response = client.chat.completions.create(
            model="gpt-4-vision-preview",
            messages=messages,
            max_tokens=500
        )

        assistant_response = response.choices[0].message.content
        st.session_state['conversation_history'].append({"role": "assistant", "content": assistant_response})
        
        st.chat_message("user").write(user_message)
        st.chat_message("assistant").write(assistant_response)




def about_page():
    st.markdown('<div class="stTitleBanner"><h1 class="stTitle">About Meal Master</h1><p class="stText">Daily Chef Meal Planner aims to revolutionize meal planning by developing one AI system that suggests recipes based on the contents of a user\'s fridge, dietary preferences, and nutritional goals. This innovative application promises to reduce food waste, enhance dietary variety, and support nutritional goals through personalized culinary suggestions. It features ingredient recognition, recipe customization, and user feedback integration to refine and personalize meal recommendations.</p></div>', unsafe_allow_html=True)

    st.markdown('<div class="stTitleBox"><h2 class="stTitle">Founders</h2><p class="stText">Meet the founders of Meal Master:</p></div>', unsafe_allow_html=True)

    # Custom CSS for captions
    st.markdown("""
    <style>
    .caption {
        font-weight: bold;
        font-size: 16px; /* Increase font size */
        color: #ffffff; /* White text color, change as needed */
        background-color: rgba(0,0,0,0.6); /* Semi-transparent black background for contrast */
        padding: 3px;
        border-radius: 5px; /* Rounded corners for the caption background */
        text-align: center; /* Center-align text */
    }

    .faq-question {
        font-weight: bold;
        font-size: 18px;
        color: #ffffff; /* White text color */
        background-color: rgba(0,0,0,0.6); /* Semi-transparent black background for contrast */
        padding: 3px;
        border-radius: 5px; /* Rounded corners for the caption background */
        margin-bottom: 10px;
    }

    .faq-answer {
        font-size: 16px;
        color: #ffffff; /* White text color */
        background-color: rgba(0,0,0,0.6); /* Semi-transparent black background for contrast */
        padding: 3px;
        border-radius: 5px; /* Rounded corners for the caption background */
        margin-bottom: 20px;
    }
    </style>
    """, unsafe_allow_html=True)

    image_filenames = ["alik.jpg", "Sne.jpg", "Yue.jpg", "Mic.jpg", "Sid.jpg"]
    captions = ["Alik Assi", "Sneha Sahu", "Yue Guo", "Michael Carter", "Sidra Imran"]

    cols = st.columns(5)
    for col, img_filename, caption in zip(cols, image_filenames, captions):
        with col:
            st.image(img_filename, width=100, output_format='JPEG', use_column_width=False)
            # Wrap the caption in a div with the class 'caption' for styling
            st.markdown(f"<div class='caption'>{caption}</div>", unsafe_allow_html=True)
    
    st.markdown('<div class="stTitleBox"><h2 class="stTitle">FAQ</h2></div>', unsafe_allow_html=True)

    # Define frequently asked questions and their answers
    faqs = [
        {"question": "1. What is Meal Master?", "answer": "Meal Master is a Daily Chef Meal Planner that uses AI to suggest recipes based on the contents of your fridge, dietary preferences, and nutritional goals."},
        {"question": "2. How does Meal Master work?", "answer": "Meal Master analyzes the ingredients in your fridge, along with your dietary preferences and nutritional goals, to generate personalized recipe recommendations."},
        {"question": "3. Who are the founders of Daily Chef?", "answer": "Meal Master was founded by Alik Assi, Sneha Sahu, Yue Guo, Michael Carter, and Sidra Imran."},
        # Add more questions and answers as needed
    ]

    # Display FAQs with improved styling
    for faq in faqs:
        st.markdown(f"<p class='faq-question'>{faq['question']}</p>", unsafe_allow_html=True)
        st.markdown(f"<p class='faq-answer'>{faq['answer']}</p>", unsafe_allow_html=True)


def review_section():
    st.markdown('<div class="stTitleBox"><h2 class="stTitle">Reviews</h2></div>', unsafe_allow_html=True)
    
    st.write("### Rate your experience")
    
    # Text input for the reviewer's name
    user_name = st.text_input("Your name", key='user_name')
    
    # Use a slider for rating
    user_rating = st.slider("Select your rating", 0, 5, 1)  # Start at 1, range is from 0 to 5
    
    # Review text input
    review_text = st.text_area("Your review", height=150, key='review_text')
    
    # Initialize the reviews list in the session state if it doesn't exist
    if 'reviews' not in st.session_state:
        st.session_state['reviews'] = []
    
    # Submit button for the review
    if st.button('Submit Review'):
        # Append the new review to the session state list
        st.session_state['reviews'].append((user_name, user_rating, review_text))
        
        # Clear the form (This won't actually clear the input boxes in Streamlit. See the note below.)
        user_name = ''  # This line is for illustrative purposes and won't clear the input box.
        review_text = ''  # This won't clear the textarea.
        
    st.write('\n')

    # Display each stored review
    if st.session_state['reviews']:
        st.write("### Past Reviews")
        for review in st.session_state['reviews']:
            if len(review) == 3:
                name, rating, text = review
                # Display each review in a card format with custom styling
                st.markdown(
                    f"""
                    <div style="background-color: #333333; color: #ffffff; padding: 15px; border-radius: 10px; margin-bottom: 20px;">
                        <p style="font-weight: bold; font-size: 18px;">Name: {name}</p>
                        <p style="font-size: 16px;">Rating: {'&#9733;' * rating}</p>
                        <p style="font-size: 16px;">Review: {text}</p>
                    </div>
                    """,
                    unsafe_allow_html=True
                )
            else:
                st.write("Review data format is incorrect.")




def main():
    # Call the function to set the background image and black banner
   

    # Navigation bar using hyperlinks
    st.sidebar.title("Navigation")
    page = st.sidebar.selectbox("Go to", ["Home", "Meal Master", "About", "Reviews"])

    if page == "Home":
        home_page()
        set_background()
    elif page == "Meal Master":
        recipe_generator()
    elif page == "About":
        about_page()
        set_background()
    elif page == "Reviews":
        review_section()
        
  
if __name__ == "__main__":
    main()
