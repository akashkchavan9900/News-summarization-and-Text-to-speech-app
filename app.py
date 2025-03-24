import streamlit as st
import requests
import json
import base64

API_URL = "http://127.0.0.1:8000" # Adjust if your API is running elsewhere


def play_audio_from_url(audio_url):
    """Plays audio from a given URL in Streamlit."""
    try:
        audio_response = requests.get(audio_url)
        audio_response.raise_for_status()
        audio_bytes = audio_response.content
        audio_base64 = base64.b64encode(audio_bytes).decode()
        audio_html = f"""
            <audio controls autoplay="false">
            <source src="data:audio/mp3;base64,{audio_base64}" type="audio/mp3">
            Your browser does not support the audio element.
            </audio>
            """
        st.markdown(audio_html, unsafe_allow_html=True)
    except requests.exceptions.RequestException as e:
        st.error(f"Error playing audio: {e}")


def main():
    st.title("Company News Sentiment Analysis")

    company_list = ["Tesla", "Amazon", "Google"] #  Ideally fetch from company_list.csv or API
    selected_company = st.selectbox("Select Company", company_list)

    if selected_company:
        api_endpoint = f"{API_URL}/company/{selected_company}"
        try:
            response = requests.get(api_endpoint)
            response.raise_for_status() # Raise HTTPError for bad responses (4xx or 5xx)
            data = response.json()

            if data:
                st.header(f"News Sentiment Analysis for {data['Company']}")

                for article in data['Articles']:
                    st.subheader(article['Title'])
                    st.write(f"**Summary:** {article['Summary']}")
                    st.write(f"**Sentiment:** {article['Sentiment']} (Score: {article['Sentiment Score']:.2f})")
                    st.write(f"**Topics:** {', '.join(article['Topics'])}")
                    st.write(f"[Read More]({article['URL']})")
                    st.markdown("---")

                st.subheader("Comparative Sentiment Analysis")
                st.write(f"**Sentiment Distribution:** {data['Comparative Sentiment Score']['Sentiment Distribution']}")
                st.write("**Coverage Differences:**")
                for diff in data['Comparative Sentiment Score']['Coverage Differences']:
                    st.write(f"- {diff['Comparison']}")
                    st.write(f"  *Impact:* {diff['Impact']}")
                st.write("**Topic Overlap:**")
                st.write(f"- **Common Topics:** {', '.join(data['Comparative Sentiment Score']['Topic Overlap']['Common Topics'])}")
                for unique_topic_key, unique_topics in data['Comparative Sentiment Score']['Topic Overlap'].items():
                    if unique_topic_key != "Common Topics":
                        st.write(f"- **{unique_topic_key}:** {', '.join(unique_topics)}")

                st.subheader("Final Sentiment Summary")
                st.write(data['Final Sentiment Analysis'])

                if data['Hindi_TTS']:
                    st.subheader("Hindi Text-to-Speech")
                    st.write(f"**Text:** {data['Hindi_TTS']['Text']}")
                    audio_url = f"{API_URL}{data['Hindi_TTS']['Audio_URL']}" # Construct full audio URL for API
                    play_audio_from_url(audio_url) # Play audio from API served URL
                else:
                    st.write("Hindi TTS unavailable.")


            else:
                st.error("No data received from API.")

        except requests.exceptions.RequestException as e:
            st.error(f"Error fetching data from API: {e}")
        except json.JSONDecodeError:
            st.error("Error decoding JSON response from API.")


if __name__ == "__main__":
    main()