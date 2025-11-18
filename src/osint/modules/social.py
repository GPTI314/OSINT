"""
Social Media Intelligence (SOCMINT) Module

Provides comprehensive social media intelligence gathering including:
- Profile discovery across platforms
- Post collection and analysis
- Connection analysis (followers/following)
- Activity tracking and patterns
- Image analysis
Supported platforms: Twitter, LinkedIn, Instagram, Facebook, TikTok, Reddit
"""

import requests
import json
from typing import Dict, Any, List, Optional
from datetime import datetime
import time

from ..core.base import BaseModule
from ..core.utils import rate_limit


class SocialMediaIntelligence(BaseModule):
    """Social Media Intelligence gathering module"""

    def __init__(self, config: Optional[Dict[str, Any]] = None):
        super().__init__(config)
        self.twitter_api_key = self.config.get('twitter_api_key')
        self.twitter_api_secret = self.config.get('twitter_api_secret')
        self.twitter_access_token = self.config.get('twitter_access_token')
        self.twitter_access_secret = self.config.get('twitter_access_secret')
        self.twitter_bearer_token = self.config.get('twitter_bearer_token')
        self.reddit_client_id = self.config.get('reddit_client_id')
        self.reddit_client_secret = self.config.get('reddit_client_secret')
        self.reddit_user_agent = self.config.get('reddit_user_agent')

    def collect(self, target: str, **kwargs) -> Dict[str, Any]:
        """
        Collect comprehensive social media intelligence

        Args:
            target: Username or profile to investigate
            **kwargs: Additional options
                - platforms: List of platforms to search (default: all)
                - include_posts: Include post collection (default: True)
                - include_connections: Include connection analysis (default: True)
                - include_activity: Include activity tracking (default: True)
                - max_posts: Maximum posts to collect (default: 100)

        Returns:
            Dictionary with comprehensive social media intelligence
        """
        try:
            platforms = kwargs.get('platforms', ['twitter', 'linkedin', 'instagram', 'facebook', 'tiktok', 'reddit'])
            data = {}

            for platform in platforms:
                self.logger.info(f"Collecting data from {platform}")
                platform_data = self._collect_platform_data(
                    platform, target, **kwargs
                )
                if platform_data:
                    data[platform] = platform_data

            return self._create_result(target=target, data=data)

        except Exception as e:
            return self._handle_error(target, e)

    def _collect_platform_data(self, platform: str, username: str, **kwargs) -> Dict[str, Any]:
        """
        Collect data from specific platform

        Args:
            platform: Platform name
            username: Username to investigate
            **kwargs: Additional options

        Returns:
            Platform-specific data
        """
        if platform == 'twitter':
            return self.collect_twitter(username, **kwargs)
        elif platform == 'reddit':
            return self.collect_reddit(username, **kwargs)
        elif platform == 'linkedin':
            return self.collect_linkedin(username, **kwargs)
        elif platform == 'instagram':
            return self.collect_instagram(username, **kwargs)
        elif platform == 'facebook':
            return self.collect_facebook(username, **kwargs)
        elif platform == 'tiktok':
            return self.collect_tiktok(username, **kwargs)
        else:
            return {'error': f'Unsupported platform: {platform}'}

    def collect_twitter(self, username: str, **kwargs) -> Dict[str, Any]:
        """
        Collect Twitter intelligence

        Args:
            username: Twitter username
            **kwargs: Additional options

        Returns:
            Twitter intelligence data
        """
        if not self.twitter_bearer_token:
            return {'error': 'Twitter API credentials not configured'}

        try:
            import tweepy

            # Authenticate
            auth = tweepy.OAuth2BearerHandler(self.twitter_bearer_token)
            api = tweepy.API(auth, wait_on_rate_limit=True)

            twitter_data = {}

            # Get user profile
            try:
                user = api.get_user(screen_name=username)
                twitter_data['profile'] = {
                    'id': user.id_str,
                    'name': user.name,
                    'screen_name': user.screen_name,
                    'description': user.description,
                    'location': user.location,
                    'url': user.url,
                    'followers_count': user.followers_count,
                    'friends_count': user.friends_count,
                    'listed_count': user.listed_count,
                    'favourites_count': user.favourites_count,
                    'statuses_count': user.statuses_count,
                    'created_at': user.created_at.isoformat(),
                    'verified': user.verified,
                    'profile_image_url': user.profile_image_url_https,
                    'profile_banner_url': user.profile_banner_url if hasattr(user, 'profile_banner_url') else None
                }
            except Exception as e:
                return {'error': f'User not found or API error: {str(e)}'}

            # Collect posts/tweets
            if kwargs.get('include_posts', True):
                max_posts = kwargs.get('max_posts', 100)
                tweets = []

                try:
                    for tweet in tweepy.Cursor(api.user_timeline, screen_name=username, tweet_mode='extended').items(max_posts):
                        tweets.append({
                            'id': tweet.id_str,
                            'created_at': tweet.created_at.isoformat(),
                            'text': tweet.full_text,
                            'retweet_count': tweet.retweet_count,
                            'favorite_count': tweet.favorite_count,
                            'lang': tweet.lang,
                            'source': tweet.source,
                            'in_reply_to': tweet.in_reply_to_screen_name,
                            'is_retweet': hasattr(tweet, 'retweeted_status'),
                            'hashtags': [tag['text'] for tag in tweet.entities.get('hashtags', [])],
                            'mentions': [mention['screen_name'] for mention in tweet.entities.get('user_mentions', [])],
                            'urls': [url['expanded_url'] for url in tweet.entities.get('urls', [])]
                        })

                    twitter_data['tweets'] = {
                        'count': len(tweets),
                        'posts': tweets
                    }
                except Exception as e:
                    twitter_data['tweets'] = {'error': str(e)}

            # Connection analysis
            if kwargs.get('include_connections', True):
                try:
                    # Get followers (limited to first 100)
                    followers = []
                    for follower in tweepy.Cursor(api.get_followers, screen_name=username).items(100):
                        followers.append({
                            'id': follower.id_str,
                            'screen_name': follower.screen_name,
                            'name': follower.name,
                            'followers_count': follower.followers_count
                        })

                    # Get following (limited to first 100)
                    following = []
                    for friend in tweepy.Cursor(api.get_friends, screen_name=username).items(100):
                        following.append({
                            'id': friend.id_str,
                            'screen_name': friend.screen_name,
                            'name': friend.name,
                            'followers_count': friend.followers_count
                        })

                    twitter_data['connections'] = {
                        'followers': {
                            'count': len(followers),
                            'sample': followers
                        },
                        'following': {
                            'count': len(following),
                            'sample': following
                        }
                    }
                except Exception as e:
                    twitter_data['connections'] = {'error': str(e)}

            # Activity analysis
            if kwargs.get('include_activity', True) and twitter_data.get('tweets'):
                tweets_list = twitter_data['tweets'].get('posts', [])
                if tweets_list:
                    # Analyze posting patterns
                    hours = [datetime.fromisoformat(t['created_at']).hour for t in tweets_list]
                    hour_distribution = {h: hours.count(h) for h in range(24)}

                    # Most used hashtags
                    all_hashtags = []
                    for tweet in tweets_list:
                        all_hashtags.extend(tweet.get('hashtags', []))
                    hashtag_freq = {}
                    for tag in all_hashtags:
                        hashtag_freq[tag] = hashtag_freq.get(tag, 0) + 1

                    twitter_data['activity'] = {
                        'posting_hours': hour_distribution,
                        'most_active_hour': max(hour_distribution, key=hour_distribution.get),
                        'top_hashtags': sorted(hashtag_freq.items(), key=lambda x: x[1], reverse=True)[:10],
                        'avg_retweets': sum(t['retweet_count'] for t in tweets_list) / len(tweets_list),
                        'avg_favorites': sum(t['favorite_count'] for t in tweets_list) / len(tweets_list)
                    }

            return twitter_data

        except Exception as e:
            self.logger.warning(f"Twitter collection failed: {str(e)}")
            return {'error': str(e)}

    def collect_reddit(self, username: str, **kwargs) -> Dict[str, Any]:
        """
        Collect Reddit intelligence

        Args:
            username: Reddit username
            **kwargs: Additional options

        Returns:
            Reddit intelligence data
        """
        if not all([self.reddit_client_id, self.reddit_client_secret, self.reddit_user_agent]):
            return {'error': 'Reddit API credentials not configured'}

        try:
            import praw

            reddit = praw.Reddit(
                client_id=self.reddit_client_id,
                client_secret=self.reddit_client_secret,
                user_agent=self.reddit_user_agent
            )

            reddit_data = {}

            # Get user profile
            try:
                user = reddit.redditor(username)
                reddit_data['profile'] = {
                    'id': user.id,
                    'name': user.name,
                    'created_utc': datetime.fromtimestamp(user.created_utc).isoformat(),
                    'link_karma': user.link_karma,
                    'comment_karma': user.comment_karma,
                    'is_gold': user.is_gold,
                    'is_mod': user.is_mod,
                    'has_verified_email': user.has_verified_email
                }
            except Exception as e:
                return {'error': f'User not found: {str(e)}'}

            # Collect posts
            if kwargs.get('include_posts', True):
                max_posts = kwargs.get('max_posts', 100)
                posts = []

                try:
                    for submission in user.submissions.new(limit=max_posts):
                        posts.append({
                            'id': submission.id,
                            'title': submission.title,
                            'subreddit': submission.subreddit.display_name,
                            'created_utc': datetime.fromtimestamp(submission.created_utc).isoformat(),
                            'score': submission.score,
                            'upvote_ratio': submission.upvote_ratio,
                            'num_comments': submission.num_comments,
                            'url': submission.url,
                            'selftext': submission.selftext[:500] if submission.selftext else '',
                            'is_self': submission.is_self,
                            'link_flair_text': submission.link_flair_text
                        })

                    reddit_data['posts'] = {
                        'count': len(posts),
                        'submissions': posts
                    }
                except Exception as e:
                    reddit_data['posts'] = {'error': str(e)}

                # Collect comments
                try:
                    comments = []
                    for comment in user.comments.new(limit=max_posts):
                        comments.append({
                            'id': comment.id,
                            'body': comment.body[:500],
                            'subreddit': comment.subreddit.display_name,
                            'created_utc': datetime.fromtimestamp(comment.created_utc).isoformat(),
                            'score': comment.score,
                            'is_submitter': comment.is_submitter,
                            'parent_id': comment.parent_id
                        })

                    reddit_data['comments'] = {
                        'count': len(comments),
                        'comments': comments
                    }
                except Exception as e:
                    reddit_data['comments'] = {'error': str(e)}

            # Activity analysis
            if kwargs.get('include_activity', True):
                # Analyze subreddit activity
                subreddits = {}
                if reddit_data.get('posts'):
                    for post in reddit_data['posts'].get('submissions', []):
                        sub = post['subreddit']
                        subreddits[sub] = subreddits.get(sub, 0) + 1

                if reddit_data.get('comments'):
                    for comment in reddit_data['comments'].get('comments', []):
                        sub = comment['subreddit']
                        subreddits[sub] = subreddits.get(sub, 0) + 1

                reddit_data['activity'] = {
                    'active_subreddits': sorted(subreddits.items(), key=lambda x: x[1], reverse=True),
                    'total_subreddits': len(subreddits)
                }

            return reddit_data

        except Exception as e:
            self.logger.warning(f"Reddit collection failed: {str(e)}")
            return {'error': str(e)}

    def collect_linkedin(self, username: str, **kwargs) -> Dict[str, Any]:
        """
        Collect LinkedIn intelligence

        Note: LinkedIn has strict API access. This provides search URLs.

        Args:
            username: LinkedIn username
            **kwargs: Additional options

        Returns:
            LinkedIn intelligence data
        """
        return {
            'profile_url': f"https://www.linkedin.com/in/{username}",
            'search_url': f"https://www.linkedin.com/search/results/people/?keywords={username}",
            'note': 'LinkedIn requires manual access or official API partnership. Use playwright for automated scraping with proper authorization.',
            'scraping_required': True
        }

    def collect_instagram(self, username: str, **kwargs) -> Dict[str, Any]:
        """
        Collect Instagram intelligence

        Args:
            username: Instagram username
            **kwargs: Additional options

        Returns:
            Instagram intelligence data
        """
        try:
            import instaloader

            L = instaloader.Instaloader()
            instagram_data = {}

            try:
                profile = instaloader.Profile.from_username(L.context, username)

                instagram_data['profile'] = {
                    'username': profile.username,
                    'user_id': profile.userid,
                    'full_name': profile.full_name,
                    'biography': profile.biography,
                    'external_url': profile.external_url,
                    'followers': profile.followers,
                    'followees': profile.followees,
                    'mediacount': profile.mediacount,
                    'is_private': profile.is_private,
                    'is_verified': profile.is_verified,
                    'profile_pic_url': profile.profile_pic_url
                }

                # Collect posts (if public)
                if not profile.is_private and kwargs.get('include_posts', True):
                    max_posts = kwargs.get('max_posts', 50)
                    posts = []

                    for post in profile.get_posts():
                        if len(posts) >= max_posts:
                            break

                        posts.append({
                            'shortcode': post.shortcode,
                            'url': f"https://www.instagram.com/p/{post.shortcode}/",
                            'caption': post.caption[:500] if post.caption else '',
                            'likes': post.likes,
                            'comments': post.comments,
                            'date': post.date_utc.isoformat(),
                            'is_video': post.is_video,
                            'typename': post.typename,
                            'location': post.location.name if post.location else None,
                            'hashtags': list(post.caption_hashtags) if post.caption_hashtags else []
                        })

                    instagram_data['posts'] = {
                        'count': len(posts),
                        'media': posts
                    }

                return instagram_data

            except Exception as e:
                return {'error': f'Profile not found or private: {str(e)}'}

        except ImportError:
            return {'error': 'instaloader not installed'}
        except Exception as e:
            self.logger.warning(f"Instagram collection failed: {str(e)}")
            return {'error': str(e)}

    def collect_facebook(self, username: str, **kwargs) -> Dict[str, Any]:
        """
        Collect Facebook intelligence

        Note: Facebook Graph API requires app approval

        Args:
            username: Facebook username
            **kwargs: Additional options

        Returns:
            Facebook intelligence data
        """
        return {
            'profile_url': f"https://www.facebook.com/{username}",
            'search_url': f"https://www.facebook.com/search/top?q={username}",
            'note': 'Facebook requires official API access or automated scraping with facebook-scraper library',
            'scraping_required': True
        }

    def collect_tiktok(self, username: str, **kwargs) -> Dict[str, Any]:
        """
        Collect TikTok intelligence

        Args:
            username: TikTok username
            **kwargs: Additional options

        Returns:
            TikTok intelligence data
        """
        return {
            'profile_url': f"https://www.tiktok.com/@{username}",
            'note': 'TikTok requires unofficial API or web scraping. Consider using TikTokApi or playwright.',
            'scraping_required': True
        }

    def discover_profiles(self, identifier: str, identifier_type: str = 'username') -> Dict[str, Any]:
        """
        Discover profiles across all platforms

        Args:
            identifier: Username, email, or phone
            identifier_type: Type of identifier (username, email, phone)

        Returns:
            Discovered profiles across platforms
        """
        platforms = {
            'twitter': f"https://twitter.com/{identifier}",
            'instagram': f"https://instagram.com/{identifier}",
            'facebook': f"https://facebook.com/{identifier}",
            'linkedin': f"https://linkedin.com/in/{identifier}",
            'github': f"https://github.com/{identifier}",
            'youtube': f"https://youtube.com/@{identifier}",
            'tiktok': f"https://tiktok.com/@{identifier}",
            'reddit': f"https://reddit.com/user/{identifier}",
            'pinterest': f"https://pinterest.com/{identifier}",
            'snapchat': f"https://snapchat.com/add/{identifier}",
            'twitch': f"https://twitch.tv/{identifier}",
            'medium': f"https://medium.com/@{identifier}",
            'tumblr': f"https://{identifier}.tumblr.com"
        }

        discovered = {}
        for platform, url in platforms.items():
            # Quick check if profile exists (HTTP status)
            try:
                response = requests.head(url, timeout=5, allow_redirects=True)
                discovered[platform] = {
                    'url': url,
                    'exists': response.status_code == 200,
                    'status_code': response.status_code
                }
            except:
                discovered[platform] = {
                    'url': url,
                    'exists': False,
                    'error': 'Connection failed'
                }

            time.sleep(0.5)  # Rate limiting

        return discovered
