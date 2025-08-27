import React, { useState, useEffect } from 'react';
import { Link as RouterLink, useNavigate } from 'react-router-dom';
import {
  Box,
  Card,
  CardContent,
  CardMedia,
  Typography,
  TextField,
  Grid,
  Chip,
  Button,
  CircularProgress,
  Alert,
  Paper,
  InputAdornment,
  Skeleton
} from '@mui/material';
import {
  Search as SearchIcon,
  CalendarToday as CalendarIcon,
  Person as PersonIcon,
  ArrowForward as ArrowForwardIcon,
  Star as StarIcon
} from '@mui/icons-material';
import { format } from 'date-fns';

const NewsList = () => {
  const [news, setNews] = useState([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState(null);
  const [searchTerm, setSearchTerm] = useState('');
  const navigate = useNavigate();

  useEffect(() => {
    fetchNews();
  }, []);

  const fetchNews = async () => {
    try {
      const response = await fetch('http://127.0.0.1:8000/landing/news/');
      if (!response.ok) throw new Error('Failed to fetch news');
      const data = await response.json();
      setNews(data.results || data);
      setLoading(false);
    } catch (err) {
      setError(err.message);
      setLoading(false);
    }
  };

  const filteredNews = news.filter(article =>
    article.title.toLowerCase().includes(searchTerm.toLowerCase()) ||
    (article.excerpt && article.excerpt.toLowerCase().includes(searchTerm.toLowerCase()))
  );

  // Add this helper function at the top of the component
const formatDate = (dateString, formatString = 'MMM dd, yyyy') => {
    if (!dateString) return 'Unknown date';
    
    try {
      let date = parseISO(dateString);
      
      if (!isValid(date)) {
        date = new Date(dateString);
      }
      
      if (!isValid(date)) {
        return 'Invalid date';
      }
      
      return format(date, formatString);
    } catch (error) {
      console.error('Date formatting error:', error);
      return 'Invalid date';
    }
  };

  const NewsCardSkeleton = () => (
    <Card sx={{ height: '100%' }}>
      <Skeleton variant="rectangular" height={200} />
      <CardContent>
        <Skeleton variant="text" height={32} />
        <Skeleton variant="text" height={24} width="60%" />
        <Skeleton variant="text" height={16} />
        <Skeleton variant="text" height={16} />
        <Box sx={{ display: 'flex', gap: 1, mt: 2 }}>
          <Skeleton variant="rounded" width={60} height={24} />
          <Skeleton variant="rounded" width={80} height={24} />
        </Box>
      </CardContent>
    </Card>
  );

  if (error) {
    return (
      <Box sx={{ display: 'flex', justifyContent: 'center', mt: 4 }}>
        <Alert severity="error" sx={{ maxWidth: 600 }}>
          <Typography variant="h6">Error loading news</Typography>
          <Typography>{error}</Typography>
          <Button onClick={fetchNews} sx={{ mt: 1 }}>
            Try Again
          </Button>
        </Alert>
      </Box>
    );
  }

  return (
    <Box>
      {/* Header Section */}
      <Paper 
        elevation={2}
        sx={{ 
          p: 4, 
          mb: 4, 
          textAlign: 'center',
          background: 'linear-gradient(135deg, #667eea 0%, #764ba2 100%)',
          color: 'white'
        }}
      >
        <Typography variant="h2" component="h1" gutterBottom fontWeight="bold">
          Latest News
        </Typography>
        <Typography variant="h6" sx={{ opacity: 0.9 }}>
          Stay updated with the latest happenings
        </Typography>
      </Paper>

      {/* Search Section */}
      <Box sx={{ mb: 4, display: 'flex', justifyContent: 'center' }}>
        <TextField
          placeholder="Search news..."
          value={searchTerm}
          onChange={(e) => setSearchTerm(e.target.value)}
          sx={{ maxWidth: 500, width: '100%' }}
          InputProps={{
            startAdornment: (
              <InputAdornment position="start">
                <SearchIcon color="action" />
              </InputAdornment>
            ),
          }}
          variant="outlined"
        />
      </Box>

      {/* News Grid */}
      <Grid container spacing={3}>
        {loading ? (
          // Loading skeletons
          Array.from(new Array(6)).map((_, index) => (
            <Grid item xs={12} sm={6} md={4} key={index}>
              <NewsCardSkeleton />
            </Grid>
          ))
        ) : filteredNews.length > 0 ? (
          filteredNews.map((article) => (
            <Grid item xs={12} sm={6} md={4} key={article.id}>
              <Card 
                sx={{ 
                  height: '100%', 
                  display: 'flex', 
                  flexDirection: 'column',
                  transition: 'transform 0.2s ease, box-shadow 0.2s ease',
                  '&:hover': {
                    transform: 'translateY(-4px)',
                    boxShadow: 4
                  }
                }}
              >
                {/* Featured Badge */}
                {article.featured && (
                  <Box
                    sx={{
                      position: 'absolute',
                      top: 12,
                      right: 12,
                      zIndex: 1,
                    }}
                  >
                    <Chip
                      icon={<StarIcon />}
                      label="Featured"
                      color="error"
                      size="small"
                      sx={{ fontWeight: 'bold' }}
                    />
                  </Box>
                )}

                {/* Featured Image */}
                {article.featured_image && (
                  <CardMedia
                    component="img"
                    height="200"
                    image={article.featured_image}
                    alt={article.featured_image_alt || article.title}
                    sx={{
                      cursor: 'pointer',
                      transition: 'transform 0.3s ease',
                      '&:hover': {
                        transform: 'scale(1.05)'
                      }
                    }}
                    onClick={() => navigate(`/news/${article.slug}`)}
                  />
                )}

                <CardContent sx={{ flexGrow: 1, display: 'flex', flexDirection: 'column' }}>
                  {/* Meta Information */}
                  <Box sx={{ display: 'flex', alignItems: 'center', mb: 2, gap: 2 }}>
                    <Box sx={{ display: 'flex', alignItems: 'center', gap: 0.5 }}>
                      <CalendarIcon fontSize="small" color="action" />
                      <Typography variant="caption" color="text.secondary">
                        {format(new Date(article.created_at), 'MMM dd, yyyy')}
                      </Typography>
                    </Box>
                    {article.author && (
                      <Box sx={{ display: 'flex', alignItems: 'center', gap: 0.5 }}>
                        <PersonIcon fontSize="small" color="action" />
                        <Typography variant="caption" color="text.secondary">
                          {article.author}
                        </Typography>
                      </Box>
                    )}
                  </Box>

                  {/* Title */}
                  <Typography 
                    variant="h6" 
                    component="h2" 
                    gutterBottom
                    sx={{
                      cursor: 'pointer',
                      '&:hover': { color: 'primary.main' },
                      display: '-webkit-box',
                      WebkitLineClamp: 2,
                      WebkitBoxOrient: 'vertical',
                      overflow: 'hidden',
                    }}
                    onClick={() => navigate(`/news/${article.slug}`)}
                  >
                    {article.title}
                  </Typography>

                  {/* Excerpt */}
                  <Typography 
                    variant="body2" 
                    color="text.secondary" 
                    sx={{ 
                      mb: 2,
                      flexGrow: 1,
                      display: '-webkit-box',
                      WebkitLineClamp: 3,
                      WebkitBoxOrient: 'vertical',
                      overflow: 'hidden',
                    }}
                    dangerouslySetInnerHTML={{ 
                      __html: article.excerpt?.replace(/<[^>]*>/g, '') || '' 
                    }}
                  />

                  {/* Tags */}
                  {article.tags && (
                    <Box sx={{ display: 'flex', flexWrap: 'wrap', gap: 0.5, mb: 2 }}>
                      {article.tags.split(',').slice(0, 3).map((tag, index) => (
                        <Chip 
                          key={index} 
                          label={tag.trim()} 
                          size="small" 
                          variant="outlined"
                          color="primary"
                        />
                      ))}
                    </Box>
                  )}

                  {/* Read More Button */}
                  <Button
                    component={RouterLink}
                    to={`/news/${article.slug}`}
                    variant="contained"
                    endIcon={<ArrowForwardIcon />}
                    sx={{ mt: 'auto' }}
                  >
                    Read More
                  </Button>
                </CardContent>
              </Card>
            </Grid>
          ))
        ) : (
          <Grid item xs={12}>
            <Paper sx={{ p: 4, textAlign: 'center' }}>
              <Typography variant="h6" gutterBottom>
                No news articles found
              </Typography>
              <Typography color="text.secondary">
                {searchTerm ? 'Try adjusting your search terms.' : 'Check back later for updates.'}
              </Typography>
            </Paper>
          </Grid>
        )}
      </Grid>
    </Box>
  );
};

export default NewsList;