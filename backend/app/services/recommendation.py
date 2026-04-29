"""
游戏推荐服务 - 基于协同过滤的推荐算法
支持冷启动策略
"""
from app import db
from app.models import GameRating, Game, User
from sqlalchemy import func
import math
from collections import defaultdict


class RecommendationService:
    """推荐系统服务类"""
    
    @staticmethod
    def calculate_user_similarity(user1_ratings, user2_ratings):
        """
        计算两个用户之间的余弦相似度
        
        Args:
            user1_ratings: 用户1的评分字典 {game_id: score}
            user2_ratings: 用户2的评分字典 {game_id: score}
            
        Returns:
            float: 相似度值 (0-1)
        """
        # 找到共同评分的游戏
        common_games = set(user1_ratings.keys()) & set(user2_ratings.keys())
        
        if len(common_games) == 0:
            return 0.0
        
        # 计算余弦相似度
        dot_product = sum(user1_ratings[game] * user2_ratings[game] for game in common_games)
        
        magnitude1 = math.sqrt(sum(score ** 2 for score in user1_ratings.values()))
        magnitude2 = math.sqrt(sum(score ** 2 for score in user2_ratings.values()))
        
        if magnitude1 == 0 or magnitude2 == 0:
            return 0.0
        
        return dot_product / (magnitude1 * magnitude2)
    
    @staticmethod
    def get_user_ratings_dict(user_id):
        """
        获取用户的评分字典
        
        Args:
            user_id: 用户ID
            
        Returns:
            dict: {game_id: overall_score}
        """
        ratings = GameRating.query.filter_by(user_id=user_id).all()
        return {r.game_id: float(r.overall_score) for r in ratings}
    
    @staticmethod
    def find_similar_users(target_user_id, top_n=10):
        """
        找到与目标用户最相似的N个用户
        
        Args:
            target_user_id: 目标用户ID
            top_n: 返回前N个相似用户
            
        Returns:
            list: [(user_id, similarity_score), ...]
        """
        target_ratings = RecommendationService.get_user_ratings_dict(target_user_id)
        
        if not target_ratings:
            return []
        
        # 获取所有有评分记录的用户
        all_users = db.session.query(GameRating.user_id).distinct().all()
        all_user_ids = [u[0] for u in all_users if u[0] != target_user_id]
        
        similarities = []
        for user_id in all_user_ids:
            user_ratings = RecommendationService.get_user_ratings_dict(user_id)
            similarity = RecommendationService.calculate_user_similarity(
                target_ratings, user_ratings
            )
            if similarity > 0:
                similarities.append((user_id, similarity))
        
        # 按相似度降序排序
        similarities.sort(key=lambda x: x[1], reverse=True)
        return similarities[:top_n]
    
    @staticmethod
    def collaborative_filtering_recommend(user_id, limit=8):
        """
        基于协同过滤的推荐算法
        
        Args:
            user_id: 用户ID (可以为None，表示未登录用户)
            limit: 推荐游戏数量
            
        Returns:
            list: 推荐的游戏ID列表
        """
        # 如果用户未登录或没有评分记录，使用冷启动策略
        if user_id is None:
            return RecommendationService.cold_start_recommend(limit)
        
        user_ratings = RecommendationService.get_user_ratings_dict(user_id)
        
        # 如果用户评分少于3个，使用冷启动策略
        if len(user_ratings) < 3:
            return RecommendationService.cold_start_recommend(limit, user_id)
        
        # 找到相似用户
        similar_users = RecommendationService.find_similar_users(user_id, top_n=10)
        
        if not similar_users:
            return RecommendationService.cold_start_recommend(limit, user_id)
        
        # 收集相似用户喜欢的游戏（加权评分）
        game_scores = defaultdict(float)
        game_weights = defaultdict(float)
        
        for similar_user_id, similarity in similar_users:
            similar_user_ratings = RecommendationService.get_user_ratings_dict(similar_user_id)
            
            for game_id, score in similar_user_ratings.items():
                # 排除用户已经评分过的游戏
                if game_id not in user_ratings:
                    # 加权评分：相似度 * 评分
                    game_scores[game_id] += similarity * score
                    game_weights[game_id] += similarity
        
        # 计算加权平均分
        recommendations = []
        for game_id, total_score in game_scores.items():
            avg_score = total_score / game_weights[game_id]
            recommendations.append((game_id, avg_score))
        
        # 按预测评分降序排序
        recommendations.sort(key=lambda x: x[1], reverse=True)
        
        # 返回前N个游戏ID
        recommended_game_ids = [game_id for game_id, _ in recommendations[:limit]]
        
        # 如果推荐数量不足，用冷启动策略补充
        if len(recommended_game_ids) < limit:
            cold_start_games = RecommendationService.cold_start_recommend(
                limit - len(recommended_game_ids), 
                user_id,
                exclude_ids=recommended_game_ids
            )
            recommended_game_ids.extend(cold_start_games)
        
        return recommended_game_ids
    
    @staticmethod
    def cold_start_recommend(limit=8, user_id=None, exclude_ids=None):
        """
        冷启动推荐策略
        
        策略组合：
        1. 高评分游戏（平均分>=8.5）
        2. 热门游戏（评分人数多）
        3. 最新游戏
        
        Args:
            limit: 推荐数量
            user_id: 用户ID（用于排除已评分游戏）
            exclude_ids: 需要排除的游戏ID列表
            
        Returns:
            list: 游戏ID列表
        """
        exclude_ids = exclude_ids or []
        
        # 获取用户已评分的游戏ID
        if user_id:
            user_rated_games = db.session.query(GameRating.game_id)\
                .filter_by(user_id=user_id).all()
            exclude_ids.extend([g[0] for g in user_rated_games])
        
        # 子查询：计算每个游戏的平均分和评分人数
        rating_stats = db.session.query(
            GameRating.game_id,
            func.avg(GameRating.overall_score).label('avg_score'),
            func.count(GameRating.id).label('rating_count')
        ).group_by(GameRating.game_id).subquery()
        
        # 查询游戏，关联评分统计
        query = db.session.query(
            Game.id,
            rating_stats.c.avg_score,
            rating_stats.c.rating_count
        ).join(rating_stats, Game.id == rating_stats.c.game_id)\
         .filter(Game.status == 'published')
        
        # 排除指定游戏
        if exclude_ids:
            query = query.filter(~Game.id.in_(exclude_ids))
        
        # 获取所有符合条件的游戏
        games = query.all()
        
        if not games:
            # 如果没有评分数据，返回最新游戏
            latest_games = Game.query.filter_by(status='published')\
                .filter(~Game.id.in_(exclude_ids) if exclude_ids else True)\
                .order_by(Game.created_at.desc())\
                .limit(limit).all()
            return [g.id for g in latest_games]
        
        # 计算综合得分：0.6 * 平均分 + 0.4 * 归一化评分人数
        max_rating_count = max(g[2] for g in games)
        
        scored_games = []
        for game_id, avg_score, rating_count in games:
            # 归一化评分人数 (0-10)
            normalized_count = (rating_count / max_rating_count) * 10 if max_rating_count > 0 else 0
            # 综合得分
            composite_score = float(avg_score) * 0.6 + normalized_count * 0.4
            scored_games.append((game_id, composite_score, float(avg_score), rating_count))
        
        # 按综合得分排序
        scored_games.sort(key=lambda x: x[1], reverse=True)
        
        return [game_id for game_id, _, _, _ in scored_games[:limit]]
    
    @staticmethod
    def get_recommended_games(user_id=None, limit=8):
        """
        获取推荐游戏的完整信息
        
        Args:
            user_id: 用户ID（可选）
            limit: 推荐数量
            
        Returns:
            list: 游戏对象列表
        """
        # 获取推荐的游戏ID
        recommended_ids = RecommendationService.collaborative_filtering_recommend(
            user_id, limit
        )
        
        if not recommended_ids:
            return []
        
        # 查询游戏详情（保持推荐顺序）
        games = Game.query.filter(Game.id.in_(recommended_ids)).all()
        
        # 按推荐顺序排序
        game_dict = {g.id: g for g in games}
        ordered_games = [game_dict[gid] for gid in recommended_ids if gid in game_dict]
        
        return ordered_games
