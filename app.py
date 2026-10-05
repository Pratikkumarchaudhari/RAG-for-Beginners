"""Run with: streamlit run app.py"""
import time
import streamlit as st
from rag.pipeline import LocalIndex, load_chunks, generate_answer, DEFAULT_MODEL

st.set_page_config(page_title='Data Governance RAG Assistant', page_icon='📚', layout='wide')
st.title('Data Governance RAG Assistant')
st.caption('A local learning project using fictional procedures. No paid inference services.')

@st.cache_resource
def get_index():
    return LocalIndex()

with st.sidebar:
    st.header('Local settings')
    folder = st.text_input('Document folder on this computer', 'sample_documents')
    model = st.text_input('Downloaded Ollama model', DEFAULT_MODEL)
    top_k = st.slider('Passages to retrieve', 1, 6, 3)
    threshold = st.slider('Minimum cosine similarity', 0.0, 0.8, 0.25, 0.05)
    st.caption('Similarity is not confidence. The default threshold is provisional.')
    retrieval_only = st.checkbox('Inspect retrieval without running the language model')
    if st.button('Build or replace local index'):
        try:
            with st.spinner('Reading documents and building the index…'):
                count = get_index().rebuild(load_chunks(folder))
            st.success(f'Indexed {count} passages.')
        except Exception as exc:
            st.error(str(exc))
    st.caption('Initial setup downloads embedding model files. Generation requires local Ollama with cloud features disabled.')

st.write('Try: Who approves access to a dataset? What information belongs in a data issue record?')
question = st.text_input('Your question', key='question')
if st.button('Search and answer', type='primary', key='ask'):
    try:
        index = get_index()
        if not index.collection.count():
            st.warning('Build the index using the sidebar first.')
        elif not question.strip():
            st.warning('Enter a question first.')
        else:
            start = time.perf_counter()
            hits = index.search(question, top_k, threshold)
            if retrieval_only:
                st.info('Retrieval inspection mode: no generated answer.')
            else:
                with st.spinner('Generating an answer on your computer…'):
                    st.subheader('Answer')
                    st.write(generate_answer(question, hits, model))
            st.caption(f'Elapsed time: {time.perf_counter()-start:.2f} seconds')
            st.subheader('Retrieved evidence')
            if not hits:
                st.info('No passages passed the retrieval threshold.')
            for i, hit in enumerate(hits, 1):
                with st.expander(f'[{i}] {hit["source"]} — page {hit["page"]} — similarity {hit["similarity"]}', expanded=True):
                    st.text(hit['text'])
            st.caption('Check whether the evidence supports the answer. Local models can still make mistakes.')
    except Exception as exc:
        st.error(str(exc))
