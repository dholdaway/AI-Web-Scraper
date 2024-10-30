import streamlit as st
from scrape import (
    scrape_website,
    extract_body_content,
    clean_body_content,
    split_dom_content,
)
from parse import parse_with_ollama
import validators

# Initialize session state for DOM content if not already present
if "dom_content" not in st.session_state:
    st.session_state.dom_content = None

# Streamlit UI
st.title("AI Web Scraper")
url = st.text_input("Enter Website URL")

# Step 1: Scrape the Website
if st.button("Scrape Website"):
    if url and validators.url(url):
        st.write("Scraping the website...")
        with st.spinner("Scraping in progress..."):
            try:
                # Scrape the website
                dom_content = scrape_website(url)
                body_content = extract_body_content(dom_content)
                cleaned_content = clean_body_content(body_content)

                # Store the DOM content in Streamlit session state
                st.session_state.dom_content = cleaned_content

                # Display the DOM content in an expandable text box
                with st.expander("View DOM Content"):
                    st.text_area("DOM Content", cleaned_content, height=300)
            except Exception as e:
                st.error(f"An error occurred while scraping: {e}")
    else:
        st.warning("Please enter a valid URL.")

# Step 2: Ask Questions About the DOM Content
if st.session_state.dom_content:
    parse_description = st.text_area("Describe what you want to parse")

    if st.button("Parse Content"):
        if parse_description:
            st.write("Parsing the content...")
            with st.spinner("Parsing in progress..."):
                try:
                    # Parse the content with Ollama
                    dom_chunks = split_dom_content(st.session_state.dom_content)
                    parsed_result = parse_with_ollama(dom_chunks, parse_description)
                    st.write(parsed_result)
                except Exception as e:
                    st.error(f"An error occurred while parsing: {e}")
        else:
            st.warning("Please provide a description for parsing.")
else:
    st.info("Please scrape a website to load DOM content.")
