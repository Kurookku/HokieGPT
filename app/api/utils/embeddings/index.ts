// import { TogetherAIEmbeddings } from '@langchain/community/embeddings/togetherai';

// export function loadEmbeddingsModel() {
//   return new TogetherAIEmbeddings({
//     apiKey: process.env.TOGETHER_AI_API_KEY,
//     modelName: 'togethercomputer/m2-bert-80M-8k-retrieval',
//   });
// }

// import { OpenAIEmbeddings } from '@langchain/community/embeddings/openai';

// export function loadEmbeddingsModel() {
//   return new OpenAIEmbeddings({
//     apiKey: process.env.OPENAI_API_KEY,
//     modelName: 'text-embedding-3-small', // OpenAI’s embedding model
//   });
// }

// import { OpenAIEmbeddings } from "@langchain/openai";

// const embeddings = new OpenAIEmbeddings({
//   apiKey: "YOUR-API-KEY", // In Node.js defaults to process.env.OPENAI_API_KEY
//   batchSize: 512, // Default value if omitted is 512. Max is 2048
//   model: "text-embedding-3-large",
// });

// const { Configuration, OpenAIApi } = require("openai");

// const configuration = new Configuration({
//   apiKey: process.env.OPENAI_API_KEY,
// });
// const openai = new OpenAIApi(configuration);

// export function loadEmbeddingsModel() {
//   return new openai.createEmbedding({
//     apiKey: process.env.OPENAI_API_KEY,
//     modelName: 'text-embedding-3-small', // OpenAI’s embedding model
//   });

const { Configuration, OpenAIApi } = require("openai");

export async function loadEmbeddingsModel(texts: string[]): Promise<number[][]> {
  const configuration = new Configuration({
    apiKey: process.env.OPENAI_API_KEY,
  });
  const openai = new OpenAIApi(configuration);

  const embeddings: number[][] = [];

  for (const text of texts) {
    const response = await openai.createEmbedding({
      model: 'text-embedding-ada-002',
      input: text,
    });
    embeddings.push(response.data.data[0].embedding);
  }

  return embeddings;
}

// Example usage (if needed):
// const texts = ["Hello world", "Machine learning is fascinating"];
// loadEmbeddingsModel(texts).then(embeddings => console.log(embeddings));