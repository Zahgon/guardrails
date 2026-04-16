import asyncio
import json
import os
import openai
from string import Template
from typing import Callable, Dict, Optional, Type, cast

from guardrails.classes import ValidationOutcome
from guardrails.document_store import DocumentStoreBase, EphemeralDocumentStore
from guardrails.embedding import EmbeddingBase, OpenAIEmbedding
from guardrails.guard import Guard
from guardrails.utils.sql_utils import create_sql_driver
from guardrails.vectordb import Faiss, VectorDBBase

REASK_PROMPT = """
You are a data scientist whose job is to write SQL queries.

${gr.complete_json_suffix_v2}

Here's schema about the database that you can use to generate the SQL query.
Try to avoid using joins if the data can be retrieved from the same table.

${db_info}

I will give you a list of examples.

${examples}

I want to create a query for the following instruction:

${nl_instruction}

For this instruction, I was given the following JSON, which has some incorrect values.

${previous_response}

Help me correct the incorrect values based on the given error messages.
"""


EXAMPLE_BOILERPLATE = """
I will give you a list of examples. Write a SQL query similar to the examples below:
"""


def example_formatter(
    input: str, output: str, output_schema: Optional[Callable] = None
) -> str:
    pass


class Text2Sql:
    def __init__(
        self,
        conn_str: str,
        schema_file: Optional[str] = None,
        examples: Optional[Dict] = None,
        embedding: Type[EmbeddingBase] = OpenAIEmbedding,
        vector_db: Type[VectorDBBase] = Faiss,
        document_store: Type[DocumentStoreBase] = EphemeralDocumentStore,
        rail_spec: Optional[str] = None,
        rail_params: Optional[Dict] = None,
        example_formatter: Callable = example_formatter,
        reask_messages: list[Dict[str, str]] = [
            {
                "role": "user",
                "content": REASK_PROMPT,
            }
        ],
        llm_api: Optional[Callable] = None,
        llm_api_kwargs: Optional[Dict] = None,
        num_relevant_examples: int = 2,
    ):
        """Initialize the text2sql application.

        Args:
            conn_str: Connection string to the database.
            schema_file: Path to the schema file. Defaults to None.
            examples: Examples to add to the document store. Defaults to None.
            embedding: Embedding to use for document store. Defaults to OpenAIEmbedding.
            vector_db: Vector database to use for the document store. Defaults to Faiss.
            document_store: Document store to use. Defaults to EphemeralDocumentStore.
            rail_spec: Path to the rail specification. Defaults to "text2sql.rail".
            example_formatter: Fn to format examples. Defaults to example_formatter.
            reask_prompt: Prompt to use for reasking. Defaults to REASK_PROMPT.
        """
        if llm_api is None:
            llm_api = openai.completions.create

        self.example_formatter = example_formatter
        self.llm_api = llm_api
        self.llm_api_kwargs = llm_api_kwargs or {"max_tokens": 512}

        # Initialize the SQL driver.
        self.sql_driver = create_sql_driver(conn=conn_str, schema_file=schema_file)
        self.sql_schema = self.sql_driver.get_schema()

        # Number of relevant examples to use for the LLM.
        self.num_relevant_examples = num_relevant_examples

        # Initialize the Guard class.
        self.guard = self._init_guard(
            conn_str,
            schema_file,
            rail_spec,
            rail_params,
            reask_messages,
        )

        # Initialize the document store.
        self.store = self._create_docstore_with_examples(
            examples, embedding, vector_db, document_store
        )

    def _init_guard(
        self,
        conn_str: str,
        schema_file: Optional[str] = None,
        rail_spec: Optional[str] = None,
        rail_params: Optional[Dict] = None,
        reask_messages: list[Dict[str, str]] = [
            {
                "role": "user",
                "content": REASK_PROMPT,
            }
        ],
    ):
        # Initialize the Guard class
        pass

    def _create_docstore_with_examples(
        self,
        examples: Optional[Dict],
        embedding: Type[EmbeddingBase],
        vector_db: Type[VectorDBBase],
        document_store: Type[DocumentStoreBase],
    ) -> Optional[DocumentStoreBase]:
        pass

    @staticmethod
    def output_schema_formatter(output) -> str:
        pass

    def __call__(self, text: str) -> Optional[str]:
        """Run text2sql on a text query and return the SQL query."""

        if self.store is not None:
            similar_examples = self.store.search(text, self.num_relevant_examples)
            similar_examples_prompt = "\n".join(
                self.example_formatter(example.text, example.metadata["ctx"])
                for example in similar_examples
            )
        else:
            similar_examples_prompt = ""

        if asyncio.iscoroutinefunction(self.llm_api):
            raise ValueError(
                "Async API is not supported in Text2SQL application. "
                "Please use a synchronous API."
            )
        else:
            if self.llm_api is None:
                return None
            try:
                response = self.guard(
                    self.llm_api,
                    prompt_params={
                        "nl_instruction": text,
                        "examples": similar_examples_prompt,
                        "db_info": str(self.sql_schema),
                    },
                    **self.llm_api_kwargs,
                )
                response = cast(ValidationOutcome, response)
                validated_output: Dict = cast(Dict, response.validated_output)
                output = validated_output["generated_sql"]
            except TypeError:
                output = None

            return output
