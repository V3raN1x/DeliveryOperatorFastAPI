import asyncio
from fastapi import APIRouter, HTTPException
from langchain_core.exceptions import OutputParserException
from mysite.chain.ticket_chain import ticket_chain
from mysite.database.ai_schemas import TicketOutputSchema, TicketInputSchema, AnswerOutputSchema, AnswerInputSchema
from mysite.chain.answer_chain import answer_chain

ai_router = APIRouter(prefix='/ai', tags=['AI Assistant' ])

@ai_router.post('/analyze/', response_model=TicketOutputSchema)
async def analyze_ticket(ticket: TicketInputSchema):
    text = ticket.text.strip()
    if not text:
        raise HTTPException(status_code=422, detail="Информация предоставляется в неверном формате")

    try:
        result = await asyncio.wait_for(
            ticket_chain.ainvoke({'message': text}), timeout=120
        )

    except TimeoutError:
        raise HTTPException(status_code=500, detail="Модели не удалось выполнить поставленную задачу")

    except OutputParserException:
        raise HTTPException(status_code=500, detail="Ответ модели не соответствует диаграмме")

    return result

@ai_router.post('/answer/', response_model=AnswerOutputSchema)
async def answer_list(answer: AnswerInputSchema):
    text = answer.text.strip()
    facts = answer.facts.strip()
    if not text:
        raise HTTPException(status_code=422, detail="Информация предоставляется в неверном формате")
    try:
        result = await asyncio.wait_for(
            answer_chain.ainvoke({'text': text, 'facts': facts}), timeout=120
        )

    except TimeoutError:
        raise HTTPException(status_code=500, detail="Модели не удалось выполнить поставленную задачу")

    except OutputParserException:
        raise HTTPException(status_code=500, detail="Ответ модели не соответствует диаграмме")

    result = result.strip()

    return AnswerOutputSchema(text_draft=result)