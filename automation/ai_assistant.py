"""AI Assistant for smart suggestions and automation."""

from typing import Dict, List, Optional, Any
from datetime import datetime
from sqlalchemy import select, func
from sqlalchemy.ext.asyncio import AsyncSession

from database.gamification_models import AIAssistantSession, UserProgress
from database.models import Investigation, ScrapingJob, Target


class AIAssistant:
    """
    AI assistant to reduce manual work:
    - Smart suggestions
    - Auto-completion
    - Predictive actions
    - Workflow recommendations
    - Error prevention
    - Time-saving shortcuts
    """

    def __init__(self, db: AsyncSession):
        self.db = db

    async def suggest_actions(self, user_id: int, context: Dict[str, Any]) -> List[Dict]:
        """
        Suggest next actions based on context.

        Args:
            user_id: User ID
            context: Current context (e.g., investigation_id, recent_actions)

        Returns:
            List of suggested actions
        """
        suggestions = []

        # Get user's recent activity
        result = await self.db.execute(
            select(Investigation)
            .where(Investigation.created_by == user_id)
            .order_by(Investigation.created_at.desc())
            .limit(5)
        )
        recent_investigations = result.scalars().all()

        # Suggest based on investigation state
        if context.get('investigation_id'):
            inv_id = context['investigation_id']
            result = await self.db.execute(
                select(Investigation).where(Investigation.id == inv_id)
            )
            investigation = result.scalar_one_or_none()

            if investigation:
                # Check if investigation has targets
                if not investigation.targets:
                    suggestions.append({
                        'action': 'add_targets',
                        'title': 'Add Targets',
                        'description': 'Add targets to start gathering intelligence',
                        'priority': 'high',
                        'estimated_time': 60  # seconds
                    })
                else:
                    # Suggest scraping jobs
                    result = await self.db.execute(
                        select(func.count(ScrapingJob.id))
                        .join(Target)
                        .join(Investigation.targets)
                        .where(Investigation.id == inv_id)
                    )
                    scrape_count = result.scalar()

                    if scrape_count == 0:
                        suggestions.append({
                            'action': 'create_scraping_job',
                            'title': 'Start Data Collection',
                            'description': 'Create scraping jobs for your targets',
                            'priority': 'high',
                            'estimated_time': 120
                        })

                # Check if investigation has findings
                if investigation.findings:
                    suggestions.append({
                        'action': 'analyze_findings',
                        'title': 'Analyze Findings',
                        'description': 'Run correlation analysis on your findings',
                        'priority': 'medium',
                        'estimated_time': 180
                    })

                    suggestions.append({
                        'action': 'generate_report',
                        'title': 'Generate Report',
                        'description': 'Create a report from your findings',
                        'priority': 'medium',
                        'estimated_time': 300
                    })

        # Suggest based on user patterns
        if len(recent_investigations) >= 3:
            # User is active, suggest collaboration
            suggestions.append({
                'action': 'join_team',
                'title': 'Join a Team',
                'description': 'Collaborate with others to boost your productivity',
                'priority': 'low',
                'estimated_time': 300
            })

        # Suggest automation if user does repetitive tasks
        result = await self.db.execute(
            select(UserProgress).where(UserProgress.user_id == user_id)
        )
        user_progress = result.scalar_one_or_none()

        if user_progress and user_progress.investigations_created >= 5:
            suggestions.append({
                'action': 'create_workflow',
                'title': 'Automate This',
                'description': 'Create a workflow to automate similar investigations',
                'priority': 'medium',
                'estimated_time': 600,
                'time_saved': 1800  # Will save 30 minutes per investigation
            })

        return suggestions

    async def auto_complete(self, partial_input: str, context_type: str) -> List[Dict]:
        """
        Auto-complete user input.

        Args:
            partial_input: Partial user input
            context_type: Type of input (target, tag, etc.)

        Returns:
            List of completion suggestions
        """
        suggestions = []

        if context_type == 'target_domain':
            # Suggest common TLDs
            common_tlds = ['.com', '.org', '.net', '.io', '.co', '.gov', '.edu']
            if '.' not in partial_input:
                suggestions = [
                    {'value': f"{partial_input}{tld}", 'description': f'Common domain {tld}'}
                    for tld in common_tlds
                ]
            else:
                # Suggest based on existing targets
                result = await self.db.execute(
                    select(Target.value)
                    .where(Target.value.ilike(f'{partial_input}%'))
                    .limit(10)
                )
                targets = result.scalars().all()
                suggestions = [
                    {'value': t, 'description': 'Previously used target'}
                    for t in targets
                ]

        elif context_type == 'tag':
            # Get popular tags
            # This would query a tags table if it existed
            common_tags = ['phishing', 'malware', 'fraud', 'scam', 'breach', 'leak']
            matching = [tag for tag in common_tags if tag.startswith(partial_input.lower())]
            suggestions = [
                {'value': tag, 'description': 'Common tag'}
                for tag in matching
            ]

        return suggestions[:10]  # Limit to 10 suggestions

    async def predict_needs(self, user_id: int, user_behavior: Dict) -> List[Dict]:
        """
        Predict what user needs next based on behavior.

        Args:
            user_id: User ID
            user_behavior: Recent user behavior data

        Returns:
            List of predicted needs
        """
        predictions = []

        # Analyze time of day
        current_hour = datetime.utcnow().hour

        if 9 <= current_hour <= 17:
            # Work hours - suggest productivity features
            predictions.append({
                'prediction': 'batch_operation',
                'title': 'Batch Processing Available',
                'description': 'Process multiple investigations at once',
                'confidence': 0.8
            })
        else:
            # Off hours - suggest scheduled tasks
            predictions.append({
                'prediction': 'scheduled_task',
                'title': 'Schedule for Tomorrow',
                'description': 'Schedule this to run during business hours',
                'confidence': 0.7
            })

        # Check if user frequently does similar tasks
        result = await self.db.execute(
            select(Investigation)
            .where(Investigation.created_by == user_id)
            .order_by(Investigation.created_at.desc())
            .limit(10)
        )
        recent_inv = result.scalars().all()

        if len(recent_inv) >= 3:
            # Check for patterns
            descriptions = [inv.description for inv in recent_inv if inv.description]
            if len(set(descriptions)) <= 2:
                # Repetitive tasks detected
                predictions.append({
                    'prediction': 'template_suggestion',
                    'title': 'Create a Template',
                    'description': 'Save time by creating a template for similar investigations',
                    'confidence': 0.9
                })

        return predictions

    async def recommend_workflows(self, task_type: str) -> List[Dict]:
        """
        Recommend workflows for a task type.

        Args:
            task_type: Type of task

        Returns:
            List of workflow recommendations
        """
        workflow_templates = {
            'domain_investigation': {
                'name': 'Complete Domain Investigation',
                'steps': [
                    'Create investigation',
                    'Add domain target',
                    'Run WHOIS lookup',
                    'Run DNS enumeration',
                    'Check SSL certificate',
                    'Scan for technologies',
                    'Enumerate subdomains',
                    'Collect findings',
                    'Generate report'
                ],
                'estimated_time': 600,
                'automation_level': 'high'
            },
            'email_investigation': {
                'name': 'Email Intelligence Gathering',
                'steps': [
                    'Create investigation',
                    'Add email target',
                    'Verify email',
                    'Check data breaches',
                    'Search social media',
                    'Find related accounts',
                    'Collect findings',
                    'Generate report'
                ],
                'estimated_time': 480,
                'automation_level': 'medium'
            },
            'company_research': {
                'name': 'Company Background Check',
                'steps': [
                    'Create investigation',
                    'Add company target',
                    'Gather company info',
                    'Find employees on LinkedIn',
                    'Check domain ownership',
                    'Analyze web presence',
                    'Check news and mentions',
                    'Collect findings',
                    'Generate report'
                ],
                'estimated_time': 900,
                'automation_level': 'medium'
            }
        }

        template = workflow_templates.get(task_type)
        if template:
            return [template]

        return []

    async def prevent_errors(self, action: str, data: Dict) -> Dict[str, Any]:
        """
        Prevent common errors before they happen.

        Args:
            action: Action being performed
            data: Action data

        Returns:
            Validation results with warnings/errors
        """
        warnings = []
        errors = []

        if action == 'create_investigation':
            # Check for missing required fields
            if not data.get('name'):
                errors.append({
                    'field': 'name',
                    'message': 'Investigation name is required'
                })

            # Check for duplicate names
            if data.get('name'):
                result = await self.db.execute(
                    select(Investigation)
                    .where(Investigation.name == data['name'])
                    .limit(1)
                )
                existing = result.scalar_one_or_none()

                if existing:
                    warnings.append({
                        'field': 'name',
                        'message': 'An investigation with this name already exists',
                        'suggestion': f"Use '{data['name']} (2)' instead"
                    })

        elif action == 'create_target':
            # Validate target value
            target_type = data.get('type')
            target_value = data.get('value')

            if target_type == 'domain':
                # Basic domain validation
                if not target_value or '.' not in target_value:
                    errors.append({
                        'field': 'value',
                        'message': 'Invalid domain format'
                    })

            elif target_type == 'email':
                # Basic email validation
                if not target_value or '@' not in target_value:
                    errors.append({
                        'field': 'value',
                        'message': 'Invalid email format'
                    })

        return {
            'valid': len(errors) == 0,
            'errors': errors,
            'warnings': warnings
        }

    async def start_session(self, user_id: int, session_type: str, context: Dict = None):
        """Start an AI assistant session."""
        session = AIAssistantSession(
            user_id=user_id,
            session_type=session_type,
            context=context or {}
        )
        self.db.add(session)
        await self.db.commit()
        await self.db.refresh(session)

        return session

    async def end_session(
        self,
        session_id: int,
        suggestions_accepted: int = 0,
        time_saved: int = 0
    ):
        """End an AI assistant session."""
        result = await self.db.execute(
            select(AIAssistantSession).where(AIAssistantSession.id == session_id)
        )
        session = result.scalar_one_or_none()

        if session:
            session.ended_at = datetime.utcnow()
            session.suggestions_accepted = suggestions_accepted
            session.time_saved = time_saved

            # Update user progress
            result = await self.db.execute(
                select(UserProgress).where(UserProgress.user_id == session.user_id)
            )
            user_progress = result.scalar_one_or_none()

            if user_progress:
                user_progress.total_time_saved += time_saved

            await self.db.commit()

    async def get_quick_actions(self, user_id: int, context: Dict = None) -> List[Dict]:
        """Get quick action suggestions."""
        actions = [
            {
                'id': 'quick_investigation',
                'title': 'Quick Investigation',
                'description': 'Start a new investigation with smart defaults',
                'icon': '🔍',
                'shortcut': 'Ctrl+N'
            },
            {
                'id': 'smart_scrape',
                'title': 'Smart Scrape',
                'description': 'AI-suggested scraping targets',
                'icon': '🕷️',
                'shortcut': 'Ctrl+S'
            },
            {
                'id': 'instant_analysis',
                'title': 'Instant Analysis',
                'description': 'Quick analysis of current data',
                'icon': '⚡',
                'shortcut': 'Ctrl+A'
            },
            {
                'id': 'quick_report',
                'title': 'Quick Report',
                'description': 'Generate report with one click',
                'icon': '📄',
                'shortcut': 'Ctrl+R'
            }
        ]

        return actions
