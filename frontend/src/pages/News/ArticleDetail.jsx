import React, { useState, useEffect } from 'react';
import { useParams, Link as RouterLink, useNavigate } from 'react-router-dom';
import {
  Box,
  Typography,
  Card,
  CardContent,
  CardMedia,
  Chip,
  Button,
  CircularProgress,
  Alert,
  Paper,
  Grid,
  Divider,
  Breadcrumbs,
  Link,
  Stack
} from '@mui/material';
import {
  ArrowBack as ArrowBackIcon,
  CalendarToday as CalendarIcon,
  Person as PersonIcon,
  Update as UpdateIcon,
  Star as StarIcon,
  ArrowForward as ArrowForwardIcon
} from '@mui/icons-material';
import { format, parseISO, isValid } from 'date-fns';

const ArticleDetail = () => {
  const { slug } = useParams();
  const navigate = useNavigate();
  const [article, setArticle] = useState(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState(null);
  const [relatedNews, setRelatedNews] = useState([]);

  // Helper function to safely format dates
  const formatDate = (dateString, formatString = 'MMMM dd, yyyy') => {
    if (!dateString) return 'Unknown date';
    
    try {
      let date = parseISO(dateString);
      
      if (!isValid(date)) {
        date = new Date(dateString);
      }
      
      if (!isValid(date)) {
        console.warn('Invalid date:', dateString);
        return 'Invalid date';
      }
      
      return format(date, formatString);
    } catch (error) {
      console.error('Date formatting error:', error, dateString);
      return 'Invalid date';
    }
  };

  useEffect(() => {
    fetchArticle();
    fetchRelatedNews();
  }, [slug]);

  const fetchArticle = async () => {
    try {
      // First, fetch all articles to find the one with the matching slug
      const response = await fetch(`http://127.0.0.1:8000/landing/news/`);
      if (!response.ok) throw new Error(`HTTP ${response.status}: Failed to fetch articles`);
      
      const data = await response.json();
      const articles = data.results || data;
      const foundArticle = articles.find(a => a.slug === slug);
      
      if (!foundArticle) {
        throw new Error(`Article with slug "${slug}" not found`);
      }

      // Now fetch the specific article by ID to get full content
      const articleResponse = await fetch(`http://127.0.0.1:8000/landing/news/${foundArticle.id}/`);
      if (!articleResponse.ok) {
        // If specific endpoint doesn't exist, use the found article
        console.log('Using article from list endpoint');
        setArticle(foundArticle);
      } else {
        const fullArticle = await articleResponse.json();
        console.log('Found full article:', fullArticle);
        console.log('Article content:', fullArticle.content);
        console.log('Article excerpt:', fullArticle.excerpt);
        console.log('Content length:', fullArticle.content ? fullArticle.content.length : 'null/undefined');
        setArticle(fullArticle);
      }
      
      setLoading(false);
    } catch (err) {
      console.error('Error fetching article:', err);
      setError(err.message);
      setLoading(false);
    }
  };

  const fetchRelatedNews = async () => {
    try {
      const response = await fetch('http://127.0.0.1:8000/landing/news/');
      if (response.ok) {
        const data = await response.json();
        const articles = data.results || data;
        // Filter out current article and get 4 random related ones
        const related = articles
          .filter(a => a.slug !== slug)
          .slice(0, 4);
        setRelatedNews(related);
      }
    } catch (err) {
      console.error('Failed to fetch related news:', err);
    }
  };

  if (loading) {
    return (
      <Box sx={{ display: 'flex', justifyContent: 'center', alignItems: 'center', minHeight: '50vh' }}>
        <Box sx={{ textAlign: 'center' }}>
          <CircularProgress size={60} />
          <Typography sx={{ mt: 2 }}>Loading article...</Typography>
        </Box>
      </Box>
    );
  }

  if (error || !article) {
    return (
      <Box sx={{ display: 'flex', justifyContent: 'center', mt: 4 }}>
        <Alert severity="error" sx={{ maxWidth: 800 }}>
          <Typography variant="h6">Error loading article</Typography>
          <Typography>{error || 'Article not found'}</Typography>
          <Button onClick={() => navigate('/news')} sx={{ mt: 1 }}>
            Back to News
          </Button>
        </Alert>
      </Box>
    );
  }

  return (
    <Box>
      {/* Breadcrumb */}
      <Breadcrumbs sx={{ mb: 3 }}>
        <Link
          component={RouterLink}
          to="/news"
          underline="hover"
          color="inherit"
          sx={{ display: 'flex', alignItems: 'center', gap: 0.5 }}
        >
          <ArrowBackIcon fontSize="small" />
          News
        </Link>
        <Typography color="text.primary" noWrap>
          {article.title}
        </Typography>
      </Breadcrumbs>

      <Grid container spacing={4}>
        {/* Main Article */}
        <Grid item xs={12} lg={8}>
          <Paper elevation={2} sx={{ overflow: 'hidden' }}>
            {/* Featured Badge */}
            {article.featured && (
              <Box sx={{ p: 2, pb: 0 }}>
                <Chip
                  icon={<StarIcon />}
                  label="Featured Article"
                  color="error"
                  variant="filled"
                  sx={{ fontWeight: 'bold' }}
                />
              </Box>
            )}

            {/* Article Header */}
            <CardContent sx={{ pt: article.featured ? 1 : 3 }}>
              <Typography 
                variant="h3" 
                component="h1" 
                gutterBottom
                sx={{ fontWeight: 'bold', color: 'text.primary' }}
              >
                {article.title}
              </Typography>

              {/* Meta Information */}
              <Stack direction="row" spacing={3} sx={{ mb: 3, flexWrap: 'wrap' }}>
                <Box sx={{ display: 'flex', alignItems: 'center', gap: 1 }}>
                  <CalendarIcon color="action" fontSize="small" />
                  <Typography variant="body2" color="text.secondary">
                    {formatDate(article.created_at)}
                  </Typography>
                </Box>

                {article.author && (
                  <Box sx={{ display: 'flex', alignItems: 'center', gap: 1 }}>
                    <PersonIcon color="action" fontSize="small" />
                    <Typography variant="body2" color="text.secondary">
                      {article.author}
                    </Typography>
                  </Box>
                )}

                {article.updated_at && article.updated_at !== article.created_at && (
                  <Box sx={{ display: 'flex', alignItems: 'center', gap: 1 }}>
                    <UpdateIcon color="action" fontSize="small" />
                    <Typography variant="body2" color="text.secondary">
                      Updated: {formatDate(article.updated_at, 'MMM dd, yyyy')}
                    </Typography>
                  </Box>
                )}
              </Stack>

              {/* Tags */}
              {article.tags && (
                <Box sx={{ mb: 3 }}>
                  <Stack direction="row" spacing={1} flexWrap="wrap">
                    {article.tags.split(',').map((tag, index) => (
                      <Chip 
                        key={index} 
                        label={tag.trim()} 
                        variant="outlined"
                        color="primary"
                        size="small"
                      />
                    ))}
                  </Stack>
                </Box>
              )}
            </CardContent>

            {/* Featured Image */}
            {article.featured_image && (
              <CardMedia
                component="img"
                height="400"
                image={article.featured_image}
                alt={article.featured_image_alt || article.title}
                sx={{ objectFit: 'cover' }}
              />
            )}

            {/* Article Content */}
            <CardContent sx={{ pt: 3 }}>
              {/* Excerpt */}
              {article.excerpt && (
                <>
                  <Typography variant="h5" gutterBottom sx={{ fontWeight: 'bold', color: 'primary.main' }}>
                    Summary
                  </Typography>
                  <Box
                    sx={{ 
                      mb: 3, 
                      p: 2,
                      backgroundColor: 'grey.50',
                      borderRadius: 2,
                      borderLeft: 4,
                      borderColor: 'primary.main',
                      '& h1, & h2, & h3, & h4, & h5, & h6': {
                        color: 'text.primary',
                        fontWeight: 'bold',
                        margin: '1rem 0 0.5rem 0',
                        fontSize: '1.2rem'
                      },
                      '& p': {
                        margin: '0.5rem 0',
                        lineHeight: 1.6,
                      },
                      '& i, & em': {
                        fontStyle: 'italic',
                      },
                      '& b, & strong': {
                        fontWeight: 'bold',
                      }
                    }}
                    dangerouslySetInnerHTML={{ __html: article.excerpt }}
                  />
                  <Divider sx={{ mb: 3 }} />
                </>
              )}

              {/* Main Content */}
              {article.content && article.content.trim() !== '' ? (
                <>
                  <Typography variant="h5" gutterBottom sx={{ fontWeight: 'bold', color: 'primary.main' }}>
                    Full Article
                  </Typography>
                  <Box
                    sx={{
                      '& h1, & h2, & h3, & h4, & h5, & h6': {
                        color: 'text.primary',
                        fontWeight: 'bold',
                        mt: 3,
                        mb: 2
                      },
                      '& h1': { fontSize: '2rem' },
                      '& h2': { fontSize: '1.75rem' },
                      '& h3': { fontSize: '1.5rem' },
                      '& p': {
                        mb: 2,
                        lineHeight: 1.8,
                        fontSize: '1.1rem'
                      },
                      '& strong': {
                        fontWeight: 'bold'
                      },
                      '& i, & em': {
                        fontStyle: 'italic'
                      },
                      '& mark': {
                        backgroundColor: '#fff3cd',
                        padding: '2px 4px',
                        borderRadius: '2px'
                      },
                      '& .marker-yellow': {
                        backgroundColor: '#fff3cd'
                      },
                      '& img': {
                        maxWidth: '100%',
                        height: 'auto',
                        borderRadius: 1,
                        my: 2
                      },
                      '& ul, & ol': {
                        mb: 2,
                        pl: 3
                      },
                      '& blockquote': {
                        borderLeft: 4,
                        borderColor: 'primary.main',
                        pl: 2,
                        py: 1,
                        backgroundColor: 'grey.50',
                        fontStyle: 'italic',
                        my: 2
                      }
                    }}
                    dangerouslySetInnerHTML={{ __html: article.content }}
                  />
                </>
              ) : (
                <Box sx={{ textAlign: 'center', py: 4 }}>
                  <Typography variant="body1" color="text.secondary">
                    No additional content available for this article.
                  </Typography>
                  {/* Debug info in development */}
                  {process.env.NODE_ENV === 'development' && (
                    <Typography variant="caption" display="block" sx={{ mt: 2 }}>
                      Debug: Content field is {article.content === null ? 'null' : 
                                               article.content === undefined ? 'undefined' : 
                                               article.content === '' ? 'empty string' : 
                                               `"${article.content}"`}
                    </Typography>
                  )}
                </Box>
              )}
            </CardContent>
          </Paper>
        </Grid>

        {/* Sidebar */}
        <Grid item xs={12} lg={4}>
          {relatedNews.length > 0 && (
            <Paper elevation={2} sx={{ p: 3, position: 'sticky', top: 24 }}>
              <Typography variant="h5" gutterBottom fontWeight="bold">
                Related News
              </Typography>
              <Divider sx={{ mb: 2 }} />
              
              <Stack spacing={2}>
                {relatedNews.map((news) => (
                  <Card 
                    key={news.id} 
                    variant="outlined"
                    sx={{ 
                      cursor: 'pointer',
                      transition: 'all 0.2s ease',
                      '&:hover': {
                        boxShadow: 2,
                        transform: 'translateY(-1px)'
                      }
                    }}
                    onClick={() => navigate(`/news/${news.slug}`)}
                  >
                    <Box sx={{ display: 'flex', alignItems: 'flex-start', p: 2 }}>
                      {news.featured_image && (
                        <CardMedia
                          component="img"
                          sx={{ width: 80, height: 80, borderRadius: 1, mr: 2 }}
                          image={news.featured_image}
                          alt={news.title}
                        />
                      )}
                      <Box sx={{ flex: 1 }}>
                        <Typography 
                          variant="subtitle2" 
                          sx={{ 
                            fontWeight: 'bold',
                            display: '-webkit-box',
                            WebkitLineClamp: 2,
                            WebkitBoxOrient: 'vertical',
                            overflow: 'hidden',
                            mb: 0.5
                          }}
                        >
                          {news.title}
                        </Typography>
                        <Typography variant="caption" color="text.secondary">
                          {formatDate(news.created_at, 'MMM dd, yyyy')}
                        </Typography>
                      </Box>
                    </Box>
                  </Card>
                ))}
              </Stack>

              <Button
                component={RouterLink}
                to="/news"
                variant="outlined"
                fullWidth
                sx={{ mt: 3 }}
                endIcon={<ArrowForwardIcon />}
              >
                View All News
              </Button>
            </Paper>
          )}
        </Grid>
      </Grid>
    </Box>
  );
};

export default ArticleDetail;