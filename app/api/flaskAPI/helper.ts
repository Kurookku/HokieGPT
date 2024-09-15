// utils/flaskAPIHelpers.ts

export async function classifyIntent(description: string) {
    try {
      const flaskResponse = await fetch('http://localhost:5000/classify-intent', {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify({
          description, // Send the user input as 'description'
        }),
      });
      const flaskData = await flaskResponse.json();
      return flaskData; // Return the response data for further use
    } catch (error) {
      console.error('Error calling classify-intent Flask API:', error);
      throw error;
    }
  }
  

export async function adjustPDF(description: string, documentStoreId: string) {
    try {
        const formData = new FormData();
        formData.append('user_id', 'user');
        formData.append('session_name', documentStoreId);
        formData.append('instruction', description);
  
        const response = await fetch('http://localhost:5001/adjust-markdown', {
            method: 'POST',
            body: formData,
          });
      
        const contentType = response.headers.get('content-type');
  
        // Check if the response is OK (status 200-299)
        if (!response.ok) {
            const text = await response.text(); // Log the text response for debugging
            throw new Error(`Error from Flask API: ${response.status} - ${text}`);
      }
  
        const data = await response.json();
        return data;
  
    } catch (error) {
      console.error('Error calling adjust-markdown Flask API:', error);
      throw error;
    }
  }

export async function convertPDF(userId: string, sessionName: string, pdfBlob: Blob) {
    const formData = new FormData();
    formData.append('user_id', userId);
    formData.append('session_name', sessionName);
    formData.append('pdf_file', pdfBlob, 'file.pdf');
  
    try {
      const response = await fetch('http://localhost:5001/convert-pdf', {
        method: 'POST',
        body: formData,
      });
  
      const contentType = response.headers.get('content-type');
  
      if (!response.ok) {
        throw new Error(`Error with Flask API: ${response.statusText}`);
      }
  
      if (contentType && contentType.includes('application/json')) {
        const result = await response.json();
        console.log('PDF converted:', result);
        return result;
      } else {
        const textResponse = await response.text();
        throw new Error(`Unexpected response format: ${textResponse}`);
      }
    } catch (error) {
      console.error('Error converting PDF:', error);
      return { error: 'Failed to convert PDF.' };
    }
  }
  
  