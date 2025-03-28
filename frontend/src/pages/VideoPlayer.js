import React, { useState, useEffect, useRef } from 'react';
import { useParams, useNavigate } from 'react-router-dom';
import { Container, Row, Col, Card, Button, Form, Tab, Tabs, Alert } from 'react-bootstrap';
import ReactPlayer from 'react-player';
import Markdown from 'markdown-to-jsx';
import api from '../services/auth';

const VideoPlayer = () => {
  const { videoId } = useParams();
  const navigate = useNavigate();
  const playerRef = useRef(null);
  
  const [loading, setLoading] = useState(true);
  const [video, setVideo] = useState(null);
  const [notes, setNotes] = useState('');
  const [quiz, setQuiz] = useState(null);
  const [quizResponses, setQuizResponses] = useState({});
  const [quizSubmitted, setQuizSubmitted] = useState(false);
  const [quizScore, setQuizScore] = useState(0);
  const [progress, setProgress] = useState(0);
  const [error, setError] = useState('');
  const [llmQuery, setLlmQuery] = useState('');
  const [llmResponse, setLlmResponse] = useState('');
  const [llmLoading, setLlmLoading] = useState(false);

  useEffect(() => {
    const fetchVideoData = async () => {
      setLoading(true);
      try {
        // Fetch video details
        const videoResponse = await api.get(`/videos/${videoId}`);
        setVideo(videoResponse.data);
        
        // Fetch video progress
        const progressResponse = await api.get(`/videos/${videoId}/progress`);
        setProgress(progressResponse.data.progress);
        
        // Fetch quiz if available
        try {
          const quizResponse = await api.get(`/videos/${videoId}/quiz`);
          setQuiz(quizResponse.data);
        } catch (error) {
          if (error.response?.status !== 404) {
            throw error;
          }
        }
      } catch (error) {
        console.error('Error fetching video data:', error);
        setError('Failed to load video data. Please try again later.');
      } finally {
        setLoading(false);
      }
    };

    fetchVideoData();
  }, [videoId]);

  const handleNoteChange = (e) => {
    setNotes(e.target.value);
    // In a real app, we would save the notes to the API
  };

  const handleQuizResponse = (questionId, response, type) => {
    if (type === 'multiple_choice') {
      setQuizResponses({
        ...quizResponses,
        [questionId]: parseInt(response)
      });
    } else {
      setQuizResponses({
        ...quizResponses,
        [questionId]: response
      });
    }
  };

  const handleQuizSubmit = async () => {
    try {
      const response = await api.post(`/videos/${videoId}/quiz/attempt`, {
        quiz_id: quiz.id,
        responses: quizResponses
      });
      
      setQuizScore(response.data.score);
      setQuizSubmitted(true);
    } catch (error) {
      console.error('Error submitting quiz:', error);
      setError('Failed to submit quiz. Please try again.');
    }
  };

  const handleLlmQuery = async () => {
    if (!llmQuery.trim()) return;

    setLlmLoading(true);
    try {
      // In a real app, we would send the query to the API
      // For now, we'll simulate a response
      setTimeout(() => {
        setLlmResponse(`Here's some information about "${llmQuery}":\n\nChinese characters, also known as Hanzi, are logograms developed for the writing of Chinese. They have been adapted to write other East Asian languages, and remain a key component of the Japanese writing system where they are known as kanji. Chinese characters are the oldest continuously used system of writing in the world.\n\nWould you like to know more about a specific aspect of Chinese characters?`);
        setLlmLoading(false);
      }, 1500);
    } catch (error) {
      console.error('Error querying LLM:', error);
      setLlmResponse('Sorry, I encountered an error processing your query. Please try again.');
      setLlmLoading(false);
    }
  };

  const handleProgress = async (state) => {
    const newProgress = Math.round((state.playedSeconds / video.duration) * 100);
    setProgress(newProgress);
    
    try {
      await api.put(`/videos/${videoId}/progress`, {
        progress: newProgress,
        last_position: state.playedSeconds
      });
    } catch (error) {
      console.error('Error updating progress:', error);
    }
  };

  if (loading) {
    return <Container className="mt-4"><div>Loading video...</div></Container>;
  }

  if (error) {
    return <Container className="mt-4"><div className="text-danger">{error}</div></Container>;
  }

  const renderVideoPlayer = () => {
    if (video.source_type === 'youtube') {
      return (
        <div className="video-container">
          <ReactPlayer
            ref={playerRef}
            url={`https://www.youtube.com/watch?v=${video.source_id}`}
            width="100%"
            height="100%"
            controls
            onProgress={handleProgress}
          />
        </div>
      );
    } else if (video.source_type === 'local') {
      return (
        <div className="video-container">
          <ReactPlayer
            ref={playerRef}
            url={`/videos/${video.source_id}`}
            width="100%"
            height="100%"
            controls
            onProgress={handleProgress}
          />
        </div>
      );
    }
    return <div>Unsupported video source</div>;
  };

  return (
    <Container className="mt-4">
      <Button 
        variant="outline-secondary" 
        className="mb-3"
        onClick={() => navigate(-1)}
      >
        &larr; Back
      </Button>

      <h1 className="mb-3">{video.title}</h1>
      <p className="text-muted">
        {video.unit.course.title} &gt; {video.unit.title}
      </p>

      {renderVideoPlayer()}

      <div className="progress mb-3">
        <div 
          className="progress-bar" 
          role="progressbar" 
          style={{ width: `${progress}%` }} 
          aria-valuenow={progress} 
          aria-valuemin="0" 
          aria-valuemax="100"
        >
          {progress}%
        </div>
      </div>

      <Tabs defaultActiveKey="notes" className="mb-4">
        <Tab eventKey="notes" title="Notes">
          <Card>
            <Card.Body>
              <Row>
                <Col md={6}>
                  <Form.Group>
                    <Form.Label>Your Notes (Markdown supported)</Form.Label>
                    <Form.Control 
                      as="textarea" 
                      rows={15} 
                      value={notes} 
                      onChange={handleNoteChange}
                      placeholder="Take notes here..."
                    />
                  </Form.Group>
                </Col>
                <Col md={6}>
                  <h5>Preview</h5>
                  <div className="notes-container markdown-content">
                    <Markdown>{notes}</Markdown>
                  </div>
                </Col>
              </Row>
            </Card.Body>
          </Card>
        </Tab>
        <Tab eventKey="quiz" title="Quiz">
          <Card>
            <Card.Body>
              <h3>{quiz.title}</h3>
              
              {quizSubmitted ? (
                <div>
                  <Alert variant={quizScore >= 70 ? "success" : "warning"}>
                    <h4>Your Score: {quizScore}%</h4>
                    {quizScore >= 70 ? 
                      "Great job! You've passed the quiz." : 
                      "You might want to review the material and try again."}
                  </Alert>
                  <Button 
                    variant="primary" 
                    onClick={() => setQuizSubmitted(false)}
                  >
                    Retake Quiz
                  </Button>
                </div>
              ) : (
                <div>
                  {quiz.questions.map((question, index) => (
                    <div key={question.id} className="quiz-question">
                      <h5>{index + 1}. {question.question_text}</h5>
                      
                      {question.question_type === 'multiple_choice' ? (
                        <Form>
                          {question.choices.map(choice => (
                            <Form.Check
                              key={choice.id}
                              type="radio"
                              id={`choice-${choice.id}`}
                              label={choice.text}
                              name={`question-${question.id}`}
                              onChange={() => handleQuizResponse(question.id, choice.id, 'multiple_choice')}
                              checked={quizResponses[question.id] === choice.id}
                            />
                          ))}
                        </Form>
                      ) : (
                        <Form.Control
                          as="textarea"
                          rows={3}
                          placeholder="Type your answer here..."
                          value={quizResponses[question.id] || ''}
                          onChange={(e) => handleQuizResponse(question.id, e.target.value, 'short_answer')}
                        />
                      )}
                    </div>
                  ))}
                  
                  <Button 
                    variant="primary" 
                    onClick={handleQuizSubmit}
                  >
                    Submit Quiz
                  </Button>
                </div>
              )}
            </Card.Body>
          </Card>
        </Tab>
        <Tab eventKey="ai" title="AI Assistant">
          <Card>
            <Card.Body>
              <h3>Ask the AI Assistant</h3>
              <p>Have questions about the content? Ask our AI assistant for help!</p>
              
              <Form.Group className="mb-3">
                <Form.Control
                  type="text"
                  placeholder="Ask a question about the video content..."
                  value={llmQuery}
                  onChange={(e) => setLlmQuery(e.target.value)}
                />
              </Form.Group>
              
              <Button 
                variant="primary" 
                onClick={handleLlmQuery}
                disabled={llmLoading || !llmQuery.trim()}
              >
                {llmLoading ? 'Thinking...' : 'Ask Question'}
              </Button>
              
              {llmResponse && (
                <div className="mt-3 p-3 bg-light rounded">
                  <h5>Response:</h5>
                  <p style={{ whiteSpace: 'pre-line' }}>{llmResponse}</p>
                </div>
              )}
            </Card.Body>
          </Card>
        </Tab>
      </Tabs>
    </Container>
  );
};

export default VideoPlayer; 