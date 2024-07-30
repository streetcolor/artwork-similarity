import streamlit as st
import io
from qdrant.vector_searcher import VectorSearch
from config import QDRANT_URL, QDRANT_KEY, EMBEDDER, COLLECTION_NAME
from PIL import Image
import requests

st.set_page_config(
    page_title="Artwork Search", layout="centered", page_icon="./images/icon.png"
)


@st.cache_resource(show_spinner=False)
def load_search_object():
    return VectorSearch(encoder_name=EMBEDDER, qdrant_url=QDRANT_URL,qdrant_key=QDRANT_KEY, collection_name=COLLECTION_NAME)


vectorsearch = load_search_object()

st.image("images/header.png")

image_bytes = None

st.markdown('### Search for artworks similar to the uploaded image.')
uploaded_file = st.file_uploader("Upload image", type=[
    "png", "jpeg", "jpg"], accept_multiple_files=False, key=None, help="upload image")


number = st.number_input("Insert a number")
st.write("The current number is ", number)


if uploaded_file:
    # To read file as bytes
    image_bytes = uploaded_file.getvalue()
    st.image(image_bytes, width=400)

if number: 
    image = Image.open(requests.get("https://media.artsper.com/artwork/{id}_1_m.jpg".format(id=int(id)), stream=True).raw)
    buf = io.BytesIO()
    image.save(buf, format='JPEG')
    image_bytes = buf.getvalue()

if image_bytes:

    k = st.slider(label='Choose how many similar images to get',min_value=1, max_value=10, step=1, value=3)

    if st.button('Search'):

        if not image_bytes:
            st.write("error")

        else:
            with st.spinner('Searching the vector database for similar artworks'):
                search_result = vectorsearch.search(
                    Image.open(io.BytesIO(image_bytes)), k)

        st.title("Image search result")
        for id, r in enumerate(search_result):
            st.subheader(f"{r['artist_name']} ")
            st.text(f"{r['price']} €")
            st.text(f"{r['description']} ")
            st.markdown(
                f"[Buy this artwork on Artsper](https://www.artsper.com/fr/oeuvres-d-art-contemporain/peinture/{id}/tropical-elegance-03)")

            url = "https://media.artsper.com/artwork/{image_name}".format(image_name=r['image_name'])

            image = Image.open(requests.get(url, stream=True).raw).resize((400, 400), Image.LANCZOS)
            st.image(image)

            st.divider()
