from typing import Any, Type, Dict
from pydantic import BaseModel, create_model
from pydantic_ai import Agent, RunContext

class ModelContent(BaseModel):
    """Input containing content and target model."""
    content: str
    model: Type[BaseModel]

doc_processor = Agent(
    'openai:gpt-4',
    deps_type=ModelContent,
    result_type=Dict[str, Any],  # Dynamic based on input model
    system_prompt="""
    You are a technical documentation processor. Your job is to:
    1. Analyze the provided content
    2. Understand the target model schema
    3. Extract information matching the model fields
    4. Return data conforming to the model structure
    
    Be precise in matching the model's field types and requirements.
    """
)

@doc_processor.tool
def get_model_schema(ctx: RunContext[ModelContent]) -> dict:
    """Get the schema of the target model."""
    return ctx.deps.model.model_json_schema()

@doc_processor.tool
def get_content(ctx: RunContext[ModelContent]) -> str:
    """Get the content to process."""
    return ctx.deps.content

def process_with_model(content: str, model: Type[BaseModel]) -> BaseModel:
    """Process content according to given model schema."""
    result = doc_processor.run_sync(
        "Extract information according to the model schema:",
        deps=ModelContent(content=content, model=model)
    )
    return model(**result.data) 