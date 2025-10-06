# Conversations

1 conversation

## Conversation 1

    - Name: Stock Analysis Huddle
    - Participants:
        - User (Client)
        - Analyst
        - News Agent
        - Moderator
    - Purpose: All participants discuss a stock-related question in a single group chat. The Moderator facilitates the discussion, calling on the Analyst and News Agent for their inputs, then synthesizes a final answer for the User.


# Roles

4 total: 3 agents + 1 user

## Role 0 (user)

    - Title: User/Client
    - Responsibility:
        - Ask initial stock-related question
        - Provide feedback on draft answers
        - Request clarifications
    - Conversations:
        - Stock Analysis Huddle

## Role 1

    - Title: Analyst
    - Responsibility:
        - Access structured stock data (prices, financials, technical indicators)
        - Perform calculations (price changes, averages, comparisons)
        - Provide quantitative insights
    - Conversations:
        - Stock Analysis Huddle

## Role 2

    - Title: News Agent
    - Responsibility:
        - Access news article database
        - Summarize recent events affecting stocks
        - Provide qualitative context and sentiment analysis
    - Conversations:
        - Stock Analysis Huddle

## Role 3

    - Title: Moderator
    - Responsibility:
        - Facilitate the group discussion
        - Synthesize inputs from Analyst and News Agent
        - Present draft answer to User
        - Handle follow-up questions
    - Conversations:
        - Stock Analysis Huddle


# Notes

This is a simplified, single-conversation design for prototyping multi-agent collaboration. All agents participate in one shared discussion thread, making it easy to observe how agents interact and build on each other's contributions.

The turn-based approach (Moderator → Analyst → News Agent → Moderator → User) ensures predictable flow and clear role separation for the prototype.
