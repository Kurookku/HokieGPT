import { NextRequest, NextResponse } from 'next/server';
import type { Message as VercelChatMessage } from 'ai';
import { createRAGChain } from '@/utils/ragChain';

import type { Document } from '@langchain/core/documents';
import { HumanMessage, AIMessage, ChatMessage } from '@langchain/core/messages';
import { ChatTogetherAI } from '@langchain/community/chat_models/togetherai';
import { type MongoClient } from 'mongodb';
import { loadRetriever } from '../utils/vector_store';
import { loadEmbeddingsModel } from '../utils/embeddings';
import { ChatOpenAI } from "@langchain/openai";

import { classifyIntent, adjustPDF } from '../flaskAPI/helper'; 
import { loadMongoDBStore } from '../utils/vector_store/mongo'; // Import the MongoDB store helper function

export const IS_FEATURE_ENABLED: boolean = true;


export const runtime =
  process.env.NEXT_PUBLIC_VECTORSTORE === 'mongodb' ? 'nodejs' : 'edge';

const formatVercelMessages = (message: VercelChatMessage) => {
  if (message.role === 'user') {
    return new HumanMessage(message.content);
  } else if (message.role === 'assistant') {
    return new AIMessage(message.content);
  } else {
    console.warn(
      `Unknown message type passed: "${message.role}". Falling back to generic message type.`,
    );
    return new ChatMessage({ content: message.content, role: message.role });
  }
};

/**
 * This handler initializes and calls a retrieval chain. It composes the chain using
 * LangChain Expression Language. See the docs for more information:
 *
 * https://js.langchain.com/docs/get_started/quickstart
 * https://js.langchain.com/docs/guides/expression_language/cookbook#conversational-retrieval-chain
 */
export async function POST(req: NextRequest) {
  let mongoDbClient: MongoClient | undefined;
  const adjust = 'false';


  try {
    const body = await req.json();
    const messages = body.messages ?? [];
    const documentStoreId = body.documentStoreId; // Get documentStoreId from the request
    console.log(body['chatId'])
    if (!messages.length) {
      throw new Error('No messages provided.');
    }
    const formattedPreviousMessages = messages
      .slice(0, -1)
      .map(formatVercelMessages);
    const currentMessageContent = messages[messages.length - 1].content;
    const chatId = body.chatId;
    
  //////////////////////////////////////////////////////////////////

    // Call Flask API to classify the intent
    const flaskData = await classifyIntent(currentMessageContent);
    const classification = String(flaskData.classification).toLowerCase();
    const justification = String(flaskData.justification).toLowerCase();
    

  // If the classification is "adjust", call the /adjust-markdown API with the document ID
  if (classification === 'adjust') {
      const adjust = 'true';

    
  
    // Get the `docstore_document_id` from metadata
    //const documentStoreId = documents[0]?.metadata?.docstore_document_id;
    const documentStoreId = body['chatId']

    if (documentStoreId) {
      // Call adjust PDF API with the document store ID
      const adjustData = await adjustPDF(currentMessageContent, documentStoreId);
      console.log('Adjusted PDF response:', adjustData);
    } else {
      console.warn('No document store ID found in the metadata.');
    }
  }

  //////////////////////////////////////////////////////////////////

    
    //const model = new ChatTogetherAI({
    //  modelName: 'mistralai/Mixtral-8x7B-Instruct-v0.1',
    //  temperature: 0,
    //});
    const model = new ChatOpenAI({
      modelName: 'gpt-4-1106-preview',
      apiKey: process.env.OPENAI_API_KEY,
      temperature: 0.1,
    });
    const embeddings = await loadEmbeddingsModel();

    let resolveWithDocuments: (value: Document[]) => void;
    const documentPromise = new Promise<Document[]>((resolve) => {
      resolveWithDocuments = resolve;
    });

    const retrieverInfo = await loadRetriever({
      chatId,
      embeddings,
      callbacks: [
        {
          handleRetrieverEnd(documents) {
            // Extract retrieved source documents so that they can be displayed as sources
            // on the frontend.
            resolveWithDocuments(documents);
            console.log('Retrieved documents:', documents);
          },
        },
      ],
    });
    console.log('retrieverInfo', retrieverInfo);
    const retriever = retrieverInfo.retriever;
    mongoDbClient = retrieverInfo.mongoDbClient;

    const ragChain = await createRAGChain(model, retriever);

    const stream = await ragChain.stream({
      input: currentMessageContent,
      chat_history: formattedPreviousMessages,
    });

    const documents = await documentPromise;
    const serializedSources = Buffer.from(
      JSON.stringify(
        documents.map((doc) => {
          return {
            pageContent: doc.pageContent.slice(0, 50) + '...',
            metadata: doc.metadata,
          };
        }),
      ),
    ).toString('base64');

    // Convert to bytes so that we can pass into the HTTP response
    const byteStream = stream.pipeThrough(new TextEncoderStream());

    return new Response(byteStream, {
      headers: {
        'x-message-index': (formattedPreviousMessages.length + 1).toString(),
        'x-sources': serializedSources,
        'x-adjust': adjust,
      },
    });
  } catch (e: any) {
    return NextResponse.json({ error: e.message }, { status: 500 });
  } finally {
    if (mongoDbClient) {
      await mongoDbClient.close();
    }
  }
}
