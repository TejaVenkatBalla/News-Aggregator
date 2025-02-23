import React, { useEffect, useState } from 'react';
import { useAuth } from '../AuthContext';
import { API_BASE_URL } from '../config';

const NewsList = () => {
  const [news, setNews] = useState([]);
  const [loading, setLoading] = useState(true);
  const { user } = useAuth();
  const imageStyle = {
    width: "100%", // Makes the image responsive
    maxWidth: "500px", // Prevents it from getting too large
    height: "auto", // Maintains aspect ratio
    borderRadius: "8px", // Adds rounded corners
    boxShadow: "0 4px 8px rgba(0, 0, 0, 0.1)", // Adds a subtle shadow
    objectFit: "cover", // Ensures the image fills the container without distortion
  };

  useEffect(() => {
    const fetchNews = async () => {
      try {
        const headers = {};
        if (user) {
          const token = localStorage.getItem('token');
          headers['Authorization'] = `Bearer ${token}`;
        }

        const response = await fetch(`${API_BASE_URL}/api/news`, {
          headers: headers
        });

        if (!response.ok) {
          throw new Error('Failed to fetch news');
        }

        const data = await response.json();
        setNews(data);
      } catch (error) {
        console.error('Error fetching news:', error);
      } finally {
        setLoading(false);
      }
    };

    fetchNews();
  }, [user]);

  if (loading) {
    return <div>Loading news...</div>;
  }

  return (
    <div className="news-list">
      {news.map((article) => (
        <div key={article.id} className="news-item">
          <h3>{article.title}</h3>
          <p>{article.summary}</p>
          <img
  src={article.imageurl && !article.imageurl.startsWith("/static") ? article.imageurl : `${API_BASE_URL}${article.imageurl || ""}`}
  alt={article.title}
  style={imageStyle}
/>

          <a href={article.url} target="_blank" rel="noopener noreferrer">
            Read more
          </a>
          <p className="source">Source: {article.source}</p>
          <p className="timestamp">
            {new Date(article.timestamp).toLocaleString()}
          </p>
        </div>
      ))}
    </div>
  );
};

export default NewsList;
