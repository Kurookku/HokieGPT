import { NextResponse } from 'next/server';
import { RecursiveCharacterTextSplitter } from 'langchain/text_splitter';
import { PDFLoader } from 'langchain/document_loaders/fs/pdf';
import prisma from '@/utils/prisma';
import { getAuth } from '@clerk/nextjs/server';
import { loadEmbeddingsModel } from '../utils/embeddings';
import { loadVectorStore } from '../utils/vector_store';
import { type MongoClient } from 'mongodb';
import { convertPDF } from '../flaskAPI/helper'; 

export async function POST(request: Request) {
  let mongoDbClient: MongoClient | null = null;

  const { fileUrl, fileName, vectorStoreId } = await request.json();

  const { userId } = getAuth(request as any);

  if (!userId) {
    return NextResponse.json({ error: 'You must be logged in to ingest data' });
  }

  const docAmount = await prisma.document.count({
    where: {
      userId,
    },
  });

  if (docAmount > 10) {
    return NextResponse.json({
      error: 'You have reached the maximum number of documents',
    });
  }

  const doc = await prisma.document.create({
    data: {
      fileName,
      fileUrl,
      userId,
    },
  });
  const namespace = doc.id;


  try {
  /////////////////////////////////////////////////////////////////////////////////////////    
    // Call the Flask API to convert the PDF to markdown
    const pdfFile = await fetch(fileUrl); // Fetch the PDF file from the URL
    const pdfBlob = await pdfFile.blob(); // Convert it to a blob to send it to the Flask API
    console.log(fileUrl)


    // Use the convertPDF function to convert the PDF via the Flask API
    const flaskResponse = await convertPDF(userId, namespace, pdfBlob);

    if (flaskResponse.error) {
      throw new Error(`PDF conversion failed: ${flaskResponse.error}`);
    }

    console.log('PDF successfully converted to markdown:', flaskResponse);

  /////////////////////////////////////////////////////////////////////////////////////////    


    /* load from remote pdf URL */
    const response = await fetch(fileUrl);
    const buffer = await response.blob();
    const loader = new PDFLoader(buffer);
    const rawDocs = await loader.load();

    /* Split text into chunks */
    const textSplitter = new RecursiveCharacterTextSplitter({
      chunkSize: 1000,
      chunkOverlap: 200,
    });
    const splitDocs = await textSplitter.splitDocuments(rawDocs);
    // Necessary for Mongo - we'll query on this later.
    for (const splitDoc of splitDocs) {
      splitDoc.metadata.docstore_document_id = namespace;
    }

    console.log('creating vector store...');

    /* create and store the embeddings in the vectorStore */
    const embeddings = loadEmbeddingsModel();

    const store = await loadVectorStore({
      namespace: doc.id,
      embeddings,
    });
    const vectorstore = store.vectorstore;
    if ('mongoDbClient' in store) {
      mongoDbClient = store.mongoDbClient;
    }

    // embed the PDF documents
    await vectorstore.addDocuments(splitDocs);
  } catch (error) {
    console.log('error', error);
    return NextResponse.json({ error: 'Failed to ingest your data' });
  } finally {
    if (mongoDbClient) {
      await mongoDbClient.close();
    }
  }

  return NextResponse.json({
    text: 'Successfully embedded pdf',
    id: namespace,
  });
}
