import streamlit as st
from email_gen import generate_cold_email

# Streamlit App Title
st.title("Cold Email Generator with Web Scraping 🚀")

# Input Section for Web Scraping Links
st.subheader("Enter Web Scraping Links")
urls = st.text_area("Add URLs (one per line):")

# Generate Emails Button
if st.button("Generate Cold Emails"):
    if urls.strip():
        st.info("Scraping websites... This may take a few moments.")

        cold_emails = []
        email_metadata = []  # To store (company, role) for each email

        # Process each URL
        for url in urls.splitlines():
            st.write(f"🔍 Scraping: {url}")
            emails, metadata = generate_cold_email(url)  # Updated function to return metadata too

            if emails:
                cold_emails.extend(emails)
                email_metadata.extend(metadata)
            else:
                st.warning(f"No emails generated from: {url}")

        # Display Cold Emails
        st.subheader("📧 Generated Cold Emails")
        if cold_emails:
            for i, (email, meta) in enumerate(zip(cold_emails, email_metadata), 1):
                company, role = meta["company"], meta["role"]
                st.write(f"**Email {i}:** {role} at {company}")
                st.text_area(f"Cold Email {i}", email, height=200)
                st.write("---")
        else:
            st.warning("No cold emails generated. Please check the URLs and try again.")

    else:
        st.warning("Please enter at least one URL.")

st.write("Add your URLs, click the button, and get cold emails instantly! 🌟")

