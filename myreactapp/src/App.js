import React,{ useState,useEffect,useRef } from 'react';
import axios from "axios";
import './App.css';
import neutral_svg from './assets/sentiment-neutral-svgrepo-com.svg'
import happy_svg from './assets/smile-circle-svgrepo-com.svg'
import sad_svg from './assets/sad-circle-svgrepo-com.svg'
function App() {

// State variables for managing input, output, and more
  const [image, setImage] = useState(null)
  const [input, setInput] = useState('');
  const [output, setOutput] = useState('')
  const [summary, setSummary] = useState('')
  const [showSummary, setShowSummary] = useState(false); 
  const [display, setDisplay] = useState('Text'); 
  const [showTextInput, setShowTextInput] = useState(true);
  const [showImageUpload, setShowImageUpload] = useState(false);
  const [showURLUpload, setShowURLUpload] = useState(false);
  const [data, setData] = useState({}); 

// Functions to handle switching between Text, Image, and URL input modes
  const handleShowTextInput = () => {
    setShowTextInput(true);
    setShowImageUpload(false);
    setShowURLUpload(false);
    setDisplay('Text');  
  };

  const handleShowImageUpload = () => {
    setShowTextInput(false); 
    setShowImageUpload(true);
    setShowURLUpload(false);
    setDisplay('Image');

  };
  const handleShowURLUpload = () => {
    setShowTextInput(false); 
    setShowImageUpload(false);
    setShowURLUpload(true);
    setDisplay('URL');

  };
 // Function to handle form submission
  const handleSubmit = async (e) => {
    e.preventDefault();
  
    try {
      let response;
  
      if (display === 'Text') {
        response = await axios.post('/api/input-output/', { input });
      } else if (display === 'URL') {
        response = await axios.post('/api/web_scraper/', { input });
      } else if (display === 'Image') {
        let formField = new FormData()
        if(image !== null) {
        formField.append('image', image)
    }
        response = await axios.post("/api/image/", formField);
      }
  
      setOutput(response.data.output);
    } catch (error) {
      console.error('Error sending data to Django API:', error);
    }
  };

  // Function to summarize content
  const SummarizeHandle = async (e) => {
    e.preventDefault();
  
    try {
      let response;
      if(display === 'Text'){
        response = await axios.post('/api/summarizer/', { input });
      }
      else if(display === 'URL'){
        response = await axios.post('/api/url_summary/', { input });
      }
      else if(display === 'Image'){
        let formField = new FormData()
        if(image !== null) {
        formField.append('image', image)
    }
        response = await axios.post("/api/img_summary/", formField);
      }
      
      
  
        setSummary(response.data.summary);
        setShowSummary(true);
    } catch (error) {
      console.error('Error sending data to Django API:', error);
    }
  };
  
// useEffect to parse and update the data when the output changes
useEffect(() => {

  if (output) {
    try {
      const responseDictionary = JSON.parse(output);
      setData(responseDictionary);
    } catch (error) {
      console.error('Error parsing JSON:', error);
    }
  }
}, [output]);

// Extract data from the API response
  const main_tag_data = data['main_tags']
  const extra_tag_data= data['extra_tags']
  const sentiment_data= data['sentiment']
  const text= data['text']


   return (
    // Header
    <div className="area">
      <ul className="circles">
                    <li></li>
                    <li></li>
                    <li></li>
                    <li></li>
                    <li></li>
                    <li></li>
                    <li></li>
                    <li></li>
                    <li></li>
                    <li></li>
            </ul>
    <div className=' pl-3'>
    <div>
    <div class="loader">
      <div class="loader-square"></div>
      <div class="loader-square"></div>
      <div class="loader-square"></div>
      <div class="loader-square"></div>
      <div class="loader-square"></div>
      <div class="loader-square"></div>
      <div class="loader-square"></div>
    </div>
    <h1 className=" pl-24 font-bold text-4xl py-6 text-slate-200">News Scout</h1>
    </div>
    {/* Tagline */}
    </div>
  
    <div className="pt-16">
        <h2 className="pl-28 text-3xl font-semibold  text-slate-200">Enter the News</h2>
    </div>
    {/* Text , Image , URL */}
    <div className="flex mt-5 space-x-4">
        <div className={"btn flex-none z-10 hover:cursor-pointer h-10 px-10  ml-28 flex items-center justify-center font-medium text-xl bg-slate-200 ${showImageUpload ? 'rounded-lg' : ''} rounded-lg"} onClick={handleShowTextInput}>
          Text
        </div>
        <div className={"btn flex-none z-10 hover:cursor-pointer px-10 flex items-center justify-center font-medium text-xl bg-slate-200 ${showImageUpload ? 'rounded-lg' : ''} rounded-lg"} onClick={handleShowImageUpload}>
          Image
        </div>       
        <div className={"btn flex-none z-10 hover:cursor-pointer px-10 flex items-center justify-center font-medium text-xl bg-slate-200 ${showImageUpload ? 'rounded-lg' : ''} rounded-lg"} onClick={handleShowURLUpload}>
          URL
        </div>       
    </div>
    {/* Input Area */}
    <div className="flex mt-1 mx-28 h-80  rounded-xl">
    {showTextInput && (
          <textarea type="text"
          value={input}
          onChange={(e) => setInput(e.target.value)} id="message" rows="4" className="block p-2.5 w-[55%] text-xl rounded-lg border text-white bg-white bg-opacity-20 backdrop-blur-lg drop-shadow-lg" placeholder="Write your news here..."></textarea>
        )}
        {showImageUpload && (
          <div className="flex rounded-lg z-10 border-4 border-dashed  flex-col items-center justify-center w-[55%]">
            <input type="file" className="form-control pl-72 w-full text-white" onChange={(e)=>setImage(e.target.files[0])}
            
           accept="image/*" />
          </div>        
          )}          
        {showURLUpload && (

              <textarea type="text"
              value={input}
              onChange={(e) => setInput(e.target.value)} id="message" rows="1" className="block z-10 p-2.5 url-textarea text-white  w-[55%] text-lg rounded-lg border bg-white bg-opacity-20 backdrop-blur-lg drop-shadow-lg" placeholder="Paste the URL here..."></textarea>

                  
          )}        
        {/*  tags */}
        <div className="flex-col space-y-20">
      {/* main tags */}
      <div className="flex  ml-10 h-4  space-x-5 ">
        <p className="flex-none flex items-center justify-center p-2 font-semibold rounded-xl  text-slate-200 text-2xl">News Category:</p>
          
        {main_tag_data && main_tag_data.map((tag, index) => (
          <p key={index} className="main_tag flex-none -mt-2  flex items-center justify-center bg-sky-500 bg-opacity-20 backdrop-blur-lg drop-shadow-lg p-5 font-semibold rounded-xl">
          {tag}
        </p>
      ))}
          
          
       
      </div>
      {/* extra tags */}
      <div className="flex ml-10 h-4  space-x-5">
        <p className="flex-none flex items-center justify-center p-2 font-semibold  text-slate-200 rounded-xl text-2xl">Keywords:</p>
        
        {extra_tag_data && extra_tag_data.map((tag, index) => (
          <p key={index} className="flex-none -mt-2  flex items-center justify-center bg-amber-100 p-5 font-semibold rounded-xl">
          {tag}
        </p>
      ))}

      </div>
      {/* sentiment score */}
      <div className="flex ml-10 h-4  space-x-5">
        <p className="flex-none flex items-center justify-center p-2 font-semibold  text-slate-200 rounded-xl text-2xl">Sentiment:</p>
        {sentiment_data === 'positive' && (
            <img className="flex h-14 -mt-5" src={happy_svg} alt="positive_score" />
          )}
        {sentiment_data === 'negative' && (
            <img className="flex h-14 -mt-5" src={sad_svg} alt="negative_score" />
          )}
        {sentiment_data === 'neutral' && (
            <img className="flex h-14 -mt-5" src={neutral_svg} alt="neutral_score" />
          )}
      </div>
    </div>
    </div>
      {/* Submit button */}
      <button className='button ml-80 mt-7' onClick={handleSubmit}>
        <span class="button-text">Submit</span> 
      <div class="fill-container"></div>
      </button>
      <button className='button ml-20' onClick={SummarizeHandle}>
      <span class="button-text">Summarize</span> 
      <div class="fill-container"></div>
      </button>
      <div className="flex mx-28 mb-14 mt-20">
        {/* summary */}
        
      <div className="flex  mb-72 ">
        {/* summary */}
        {showSummary && (
          <div className='-mt-5'>
              <h1 className='text-white text-2xl font-semibold'>Summary:</h1>
        <div className="flex-none h-52 w-7/12 bg-white bg-opacity-20 backdrop-blur-lg drop-shadow-lg rounded-lg overscroll-y-contain">
          <p className="text-white mx-5 my-3 pt-6 text-xl">{summary}</p>
        </div>
        </div>
      
    )}
    </div>
    </div>
    </div>
  );
}

export default App;
