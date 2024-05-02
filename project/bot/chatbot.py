import asyncio

import numpy as np

from project.config import settings
import pandas as pd


class ChatBot:
    chat_history = []

    def __init__(self, memory=None):
        if memory is None:
            memory = []
        self.chat_history = memory

    @staticmethod
    async def _convert_to_embeddings(query: str):
        response = await settings.OPENAI_CLIENT.embeddings.create(
            input=query,
            model='text-embedding-3-large'
        )
        embeddings = response.data[0].embedding
        return embeddings

    @staticmethod
    async def _get_context_data(query: list[float]) -> str:
        query = np.array([query]).astype('float32')
        _, distances, indices = settings.FAISS_INDEX.range_search(query.astype('float32'), settings.SEARCH_RADIUS)
        indices_distances_df = pd.DataFrame({'index': indices, 'distance': distances})
        filtered_data_df = settings.products_dataset.iloc[indices]
        filtered_data_df['distance'] = indices_distances_df['distance'].values
        sorted_data_df: pd.DataFrame = filtered_data_df.sort_values(by='distance').reset_index(drop=True)
        sorted_data_df = sorted_data_df.drop('distance', axis=1)
        data = sorted_data_df.head(1).to_dict(orient='records')
        context_str = ''
        for row in data:
            context_str += f'{row["chunk"]}\n\n'
        return context_str

    async def _rag(self, query: str, context: str):
        self.chat_history.append({'role': 'assistant', 'content': context})
        self.chat_history.append({
            'role': 'user',
            'content': query
        })
        messages = [
            {
                'role': 'system',
                'content': f"{settings.QA_PROMPT}"
            },
        ]
        messages += self.chat_history
        stream = await settings.OPENAI_CLIENT.chat.completions.create(
            messages=messages,
            temperature=0.1,
            n=1,
            model="gpt-4-0125-preview",
            stream=True
        )
        response = ''
        async for chunk in stream:
            if chunk.choices[0].delta.content is not None:
                chunk_content = chunk.choices[0].delta.content
                response += chunk_content
                yield response
                await asyncio.sleep(0.02)
        # self.chat_history.append({'role': 'assistant', 'content': response})

    async def ask(self, question: str):
        transformed_query = await self._convert_to_embeddings(question)
        context = await self._get_context_data(transformed_query)
        async for chunk in self._rag(question, context):
            yield chunk
