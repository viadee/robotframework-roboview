"""HTML report exporter using Jinja2."""

import logging
from datetime import UTC, datetime
from pathlib import Path

from jinja2 import Template
from roboview.schemas.domain.reports import Report, SummaryReport

logger = logging.getLogger(__name__)

# Comprehensive HTML template for Summary Report
HTML_TEMPLATE = """<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>{{ title }}</title>
    <style>
        * {
            margin: 0;
            padding: 0;
            box-sizing: border-box;
        }

        body {
            font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, 'Helvetica Neue', Arial, sans-serif;
            background: linear-gradient(135deg, #1e3a5f 0%, #0f172a 100%);
            color: #334155;
            line-height: 1.6;
            min-height: 100vh;
            padding: 20px;
        }

        .container {
            max-width: 1400px;
            margin: 0 auto;
            background: white;
            border-radius: 16px;
            box-shadow: 0 25px 80px rgba(0,0,0,0.4);
            overflow: hidden;
        }

        /* Header */
        .header {
            background: linear-gradient(135deg, #1e40af 0%, #0f172a 100%);
            color: white;
            padding: 50px 40px;
        }

        .header h1 {
            font-size: 2.2em;
            margin-bottom: 8px;
            font-weight: 700;
        }

        .header .subtitle {
            font-size: 1em;
            opacity: 0.85;
            margin-bottom: 25px;
        }

        .header .metadata-grid {
            display: grid;
            grid-template-columns: repeat(auto-fit, minmax(180px, 1fr));
            gap: 15px;
            font-size: 0.85em;
        }

        .header .metadata-item {
            background: rgba(255,255,255,0.1);
            padding: 12px 15px;
            border-radius: 8px;
        }

        .header .metadata-item strong {
            display: block;
            opacity: 0.7;
            font-size: 0.8em;
            margin-bottom: 4px;
            text-transform: uppercase;
            letter-spacing: 0.5px;
        }

        /* Content */
        .content {
            padding: 40px;
        }

        .section {
            margin-bottom: 50px;
        }

        .section-header {
            display: flex;
            align-items: center;
            gap: 12px;
            margin-bottom: 25px;
            padding-bottom: 15px;
            border-bottom: 2px solid #e2e8f0;
        }

        .section-header h2 {
            font-size: 1.5em;
            color: #0f172a;
            font-weight: 600;
        }

        .section-header .badge {
            background: #1e40af;
            color: white;
            padding: 4px 12px;
            border-radius: 20px;
            font-size: 0.75em;
            font-weight: 600;
        }

        /* Health Status Box */
        .health-box {
            display: grid;
            grid-template-columns: auto 1fr;
            gap: 30px;
            padding: 30px;
            border-radius: 12px;
            margin-bottom: 30px;
        }

        .health-box.OPTIMAL {
            background: linear-gradient(135deg, #dcfce7 0%, #bbf7d0 100%);
            border: 2px solid #22c55e;
        }
        .health-box.LOW {
            background: linear-gradient(135deg, #dbeafe 0%, #bfdbfe 100%);
            border: 2px solid #3b82f6;
        }
        .health-box.MEDIUM {
            background: linear-gradient(135deg, #fef3c7 0%, #fde68a 100%);
            border: 2px solid #f59e0b;
        }
        .health-box.HIGH {
            background: linear-gradient(135deg, #fed7aa 0%, #fdba74 100%);
            border: 2px solid #f97316;
        }
        .health-box.CRITICAL {
            background: linear-gradient(135deg, #fecaca 0%, #fca5a5 100%);
            border: 2px solid #ef4444;
        }

        .health-indicator {
            display: flex;
            flex-direction: column;
            align-items: center;
            justify-content: center;
            min-width: 120px;
        }

        .health-indicator .risk-level {
            font-size: 1.8em;
            font-weight: 800;
            margin-bottom: 5px;
        }

        .health-indicator .risk-label {
            font-size: 0.75em;
            text-transform: uppercase;
            letter-spacing: 1px;
            opacity: 0.8;
        }

        .health-box.OPTIMAL .risk-level { color: #16a34a; }
        .health-box.LOW .risk-level { color: #2563eb; }
        .health-box.MEDIUM .risk-level { color: #d97706; }
        .health-box.HIGH .risk-level { color: #ea580c; }
        .health-box.CRITICAL .risk-level { color: #dc2626; }

        .health-content {
            display: flex;
            flex-direction: column;
            justify-content: center;
        }

        .health-content .status-text {
            font-size: 1.1em;
            color: #1e293b;
            margin-bottom: 10px;
        }

        .health-content .score-bar {
            display: flex;
            align-items: center;
            gap: 15px;
        }

        .health-content .score-bar .score {
            font-size: 1.5em;
            font-weight: 700;
            color: #1e40af;
        }

        .health-content .progress {
            flex: 1;
            height: 10px;
            background: rgba(0,0,0,0.1);
            border-radius: 5px;
            overflow: hidden;
        }

        .health-content .progress-fill {
            height: 100%;
            border-radius: 5px;
            background: linear-gradient(90deg, #1e40af 0%, #3b82f6 100%);
        }

        /* KPI Grid */
        .kpi-grid {
            display: grid;
            grid-template-columns: repeat(auto-fit, minmax(200px, 1fr));
            gap: 20px;
        }

        .kpi-card {
            background: #f8fafc;
            border: 1px solid #e2e8f0;
            border-radius: 12px;
            padding: 20px;
            position: relative;
            overflow: hidden;
        }

        .kpi-card::before {
            content: '';
            position: absolute;
            top: 0;
            left: 0;
            right: 0;
            height: 4px;
            background: #1e40af;
        }

        .kpi-card.warning::before { background: #f59e0b; }
        .kpi-card.danger::before { background: #ef4444; }
        .kpi-card.success::before { background: #22c55e; }

        .kpi-card .label {
            font-size: 0.8em;
            color: #64748b;
            text-transform: uppercase;
            letter-spacing: 0.5px;
            margin-bottom: 8px;
        }

        .kpi-card .value {
            font-size: 2em;
            font-weight: 700;
            color: #0f172a;
        }

        .kpi-card .progress {
            margin-top: 10px;
            height: 6px;
            background: #e2e8f0;
            border-radius: 3px;
            overflow: hidden;
        }

        .kpi-card .progress-fill {
            height: 100%;
            background: #1e40af;
            border-radius: 3px;
        }

        /* Recommendations */
        .recommendation-list {
            display: flex;
            flex-direction: column;
            gap: 15px;
        }

        .recommendation {
            display: flex;
            gap: 15px;
            padding: 20px;
            border-radius: 10px;
            background: #f8fafc;
            border-left: 4px solid #1e40af;
        }

        .recommendation.HIGH { border-left-color: #ef4444; background: #fef2f2; }
        .recommendation.MEDIUM { border-left-color: #f59e0b; background: #fffbeb; }
        .recommendation.LOW { border-left-color: #3b82f6; background: #eff6ff; }

        .recommendation .priority-badge {
            flex-shrink: 0;
            padding: 6px 12px;
            border-radius: 6px;
            font-size: 0.75em;
            font-weight: 700;
            text-transform: uppercase;
            height: fit-content;
        }

        .recommendation.HIGH .priority-badge { background: #ef4444; color: white; }
        .recommendation.MEDIUM .priority-badge { background: #f59e0b; color: white; }
        .recommendation.LOW .priority-badge { background: #3b82f6; color: white; }

        .recommendation .rec-content {
            flex: 1;
        }

        .recommendation .category {
            font-weight: 600;
            color: #0f172a;
            margin-bottom: 5px;
        }

        .recommendation .message {
            color: #475569;
        }

        .recommendation .details {
            margin-top: 8px;
            font-size: 0.9em;
            color: #64748b;
            font-style: italic;
        }

        /* Tables */
        table {
            width: 100%;
            border-collapse: collapse;
            margin-top: 15px;
            background: white;
            border-radius: 10px;
            overflow: hidden;
            box-shadow: 0 1px 3px rgba(0,0,0,0.1);
        }

        table thead {
            background: #1e40af;
            color: white;
        }

        table th {
            padding: 14px 16px;
            text-align: left;
            font-weight: 600;
            font-size: 0.85em;
            text-transform: uppercase;
            letter-spacing: 0.5px;
        }

        table td {
            padding: 12px 16px;
            border-bottom: 1px solid #e2e8f0;
            font-size: 0.9em;
        }

        table tbody tr:hover {
            background: #f8fafc;
        }

        table tbody tr:last-child td {
            border-bottom: none;
        }

        .badge-count {
            display: inline-block;
            background: #e2e8f0;
            color: #475569;
            padding: 2px 10px;
            border-radius: 12px;
            font-size: 0.85em;
            font-weight: 600;
        }

        /* Severity badges */
        .severity-badge {
            display: inline-block;
            padding: 3px 10px;
            border-radius: 4px;
            font-size: 0.75em;
            font-weight: 600;
            text-transform: uppercase;
        }

        .severity-badge.ERROR { background: #fecaca; color: #991b1b; }
        .severity-badge.WARNING { background: #fef3c7; color: #92400e; }
        .severity-badge.INFO { background: #dbeafe; color: #1e40af; }

        /* Issue distribution */
        .issue-grid {
            display: grid;
            grid-template-columns: repeat(auto-fit, minmax(250px, 1fr));
            gap: 20px;
        }

        .issue-card {
            background: #f8fafc;
            border: 1px solid #e2e8f0;
            border-radius: 10px;
            padding: 20px;
        }

        .issue-card h4 {
            font-size: 0.9em;
            color: #64748b;
            margin-bottom: 15px;
            text-transform: uppercase;
            letter-spacing: 0.5px;
        }

        .issue-bar {
            display: flex;
            align-items: center;
            gap: 10px;
            margin-bottom: 8px;
        }

        .issue-bar .name {
            flex: 1;
            font-size: 0.9em;
            color: #334155;
        }

        .issue-bar .count {
            font-weight: 600;
            color: #0f172a;
        }

        .issue-bar .bar {
            width: 80px;
            height: 6px;
            background: #e2e8f0;
            border-radius: 3px;
            overflow: hidden;
        }

        .issue-bar .bar-fill {
            height: 100%;
            background: #1e40af;
            border-radius: 3px;
        }

        /* Footer */
        .footer {
            background: #0f172a;
            color: white;
            padding: 30px 40px;
            text-align: center;
        }

        .footer .brand {
            font-size: 1.1em;
            font-weight: 600;
            margin-bottom: 8px;
        }

        .footer .generated {
            font-size: 0.85em;
            opacity: 0.7;
        }

        /* Print styles */
        @media print {
            body {
                background: white;
                padding: 0;
            }

            .container {
                box-shadow: none;
                border-radius: 0;
            }

            .section {
                page-break-inside: avoid;
            }

            table {
                page-break-inside: avoid;
            }
        }

        /* Responsive */
        @media (max-width: 768px) {
            .header { padding: 30px 20px; }
            .content { padding: 20px; }
            .health-box { grid-template-columns: 1fr; text-align: center; }
        }
    </style>
</head>
<body>
    <div class="container">
        <!-- Header -->
        <div class="header">
            <h1>{{ title }}</h1>
            <div class="subtitle">Comprehensive Robot Framework Project Analysis</div>
            <div class="metadata-grid">
                <div class="metadata-item">
                    <strong>Project</strong>
                    {{ project_name }}
                </div>
                <div class="metadata-item">
                    <strong>Analysis Date</strong>
                    {{ analysis_date }}
                </div>
                {% if author %}
                <div class="metadata-item">
                    <strong>Prepared By</strong>
                    {{ author }}
                </div>
                {% endif %}
                <div class="metadata-item">
                    <strong>RoboView Version</strong>
                    {{ roboview_version }}
                </div>
            </div>
        </div>

        <div class="content">
            <!-- Health Assessment -->
            <div class="section">
                <div class="section-header">
                    <h2>Project Health Assessment</h2>
                </div>
                <div class="health-box {{ risk_level }}">
                    <div class="health-indicator">
                        <div class="risk-level">{{ risk_level }}</div>
                        <div class="risk-label">Risk Level</div>
                    </div>
                    <div class="health-content">
                        <div class="status-text">{{ health_status }}</div>
                        <div class="score-bar">
                            <span class="score">{{ overall_score|round(1) }}/100</span>
                            <div class="progress">
                                <div class="progress-fill" style="width: {{ overall_score }}%"></div>
                            </div>
                        </div>
                    </div>
                </div>
            </div>

            <!-- Key Performance Indicators -->
            <div class="section">
                <div class="section-header">
                    <h2>Key Performance Indicators</h2>
                </div>
                <div class="kpi-grid">
                    <div class="kpi-card">
                        <div class="label">Total Keywords</div>
                        <div class="value">{{ total_keywords }}</div>
                    </div>
                    <div class="kpi-card
                        {%- if unused_keywords > 10 %} danger
                        {%- elif unused_keywords > 5 %} warning{% endif %}">
                        <div class="label">Unused Keywords</div>
                        <div class="value">{{ unused_keywords }}</div>
                    </div>
                    <div class="kpi-card
                        {%- if reusage_rate >= 70 %} success
                        {%- elif reusage_rate < 40 %} warning{% endif %}">
                        <div class="label">Keyword Reusage Rate</div>
                        <div class="value">{{ reusage_rate|round(1) }}%</div>
                        <div class="progress">
                            <div class="progress-fill" style="width: {{ reusage_rate }}%"></div>
                        </div>
                    </div>
                    <div class="kpi-card
                        {%- if documentation_coverage >= 80 %} success
                        {%- elif documentation_coverage < 50 %} warning{% endif %}">
                        <div class="label">Documentation Coverage</div>
                        <div class="value">{{ documentation_coverage|round(1) }}%</div>
                        <div class="progress">
                            <div class="progress-fill" style="width: {{ documentation_coverage }}%"></div>
                        </div>
                    </div>
                    <div class="kpi-card
                        {%- if robocop_issues == 0 %} success
                        {%- elif robocop_issues > 20 %} danger
                        {%- elif robocop_issues > 5 %} warning{% endif %}">
                        <div class="label">Code Quality Issues</div>
                        <div class="value">{{ robocop_issues }}</div>
                    </div>
                    <div class="kpi-card">
                        <div class="label">Total Files Analyzed</div>
                        <div class="value">{{ total_files }}</div>
                    </div>
                </div>
            </div>

            <!-- Recommendations -->
            {% if recommendations %}
            <div class="section">
                <div class="section-header">
                    <h2>Actionable Recommendations</h2>
                    <span class="badge">{{ recommendations|length }} items</span>
                </div>
                <div class="recommendation-list">
                    {% for rec in recommendations %}
                    <div class="recommendation {{ rec.priority }}">
                        <span class="priority-badge">{{ rec.priority }}</span>
                        <div class="rec-content">
                            <div class="category">{{ rec.category }}</div>
                            <div class="message">{{ rec.message }}</div>
                            {% if rec.details %}
                            <div class="details">{{ rec.details }}</div>
                            {% endif %}
                        </div>
                    </div>
                    {% endfor %}
                </div>
            </div>
            {% endif %}

            <!-- Most Used Keywords -->
            {% if most_used_keywords %}
            <div class="section">
                <div class="section-header">
                    <h2>Most Used Keywords</h2>
                    <span class="badge">Top {{ most_used_keywords|length }}</span>
                </div>
                <table>
                    <thead>
                        <tr>
                            <th>Keyword Name</th>
                            <th>File</th>
                            <th style="text-align: center;">Usages</th>
                            <th>Documentation</th>
                        </tr>
                    </thead>
                    <tbody>
                        {% for kw in most_used_keywords %}
                        <tr>
                            <td><strong>{{ kw.keyword_name }}</strong></td>
                            <td>{{ kw.file_name }}</td>
                            <td style="text-align: center;">
                                <span class="badge-count">{{ kw.usage_count }}</span>
                            </td>
                            <td>
                                {%- if kw.documentation and kw.documentation|length > 80 -%}
                                    {{ kw.documentation[:80] }}...
                                {%- else -%}
                                    {{ kw.documentation or '—' }}
                                {%- endif -%}
                            </td>
                        </tr>
                        {% endfor %}
                    </tbody>
                </table>
            </div>
            {% endif %}

            <!-- Unused Keywords -->
            {% if unused_keywords_list %}
            <div class="section">
                <div class="section-header">
                    <h2>Unused Keywords</h2>
                    <span class="badge">{{ unused_keywords_list|length }} candidates for removal</span>
                </div>
                <table>
                    <thead>
                        <tr>
                            <th>Keyword Name</th>
                            <th>File</th>
                            <th>Line</th>
                        </tr>
                    </thead>
                    <tbody>
                        {% for kw in unused_keywords_list %}
                        <tr>
                            <td><strong>{{ kw.keyword_name }}</strong></td>
                            <td>{{ kw.file_name }}</td>
                            <td>{{ kw.line_number or '—' }}</td>
                        </tr>
                        {% endfor %}
                    </tbody>
                </table>
            </div>
            {% endif %}

            <!-- Undocumented Keywords -->
            {% if undocumented_keywords %}
            <div class="section">
                <div class="section-header">
                    <h2>Keywords Missing Documentation</h2>
                    <span class="badge">{{ undocumented_keywords|length }} keywords</span>
                </div>
                <table>
                    <thead>
                        <tr>
                            <th>Keyword Name</th>
                            <th>File</th>
                            <th style="text-align: center;">Usages</th>
                        </tr>
                    </thead>
                    <tbody>
                        {% for kw in undocumented_keywords[:20] %}
                        <tr>
                            <td><strong>{{ kw.keyword_name }}</strong></td>
                            <td>{{ kw.file_name }}</td>
                            <td style="text-align: center;">{{ kw.usage_count }}</td>
                        </tr>
                        {% endfor %}
                        {% if undocumented_keywords|length > 20 %}
                        <tr>
                            <td colspan="3" style="text-align: center; color: #64748b; font-style: italic;">
                                ... and {{ undocumented_keywords|length - 20 }} more keywords
                            </td>
                        </tr>
                        {% endif %}
                    </tbody>
                </table>
            </div>
            {% endif %}

            <!-- Similar/Duplicate Keywords -->
            {% if duplicate_keywords %}
            <div class="section">
                <div class="section-header">
                    <h2>Similar Keywords (Refactoring Candidates)</h2>
                    <span class="badge">{{ duplicate_keywords|length }} pairs</span>
                </div>
                <table>
                    <thead>
                        <tr>
                            <th>Keyword 1</th>
                            <th>Keyword 2</th>
                            <th style="text-align: center;">Similarity</th>
                        </tr>
                    </thead>
                    <tbody>
                        {% for dup in duplicate_keywords %}
                        <tr>
                            <td>
                                <strong>{{ dup.keyword1_name }}</strong><br>
                                <small style="color: #64748b;">{{ dup.keyword1_file }}</small>
                            </td>
                            <td>
                                <strong>{{ dup.keyword2_name }}</strong><br>
                                <small style="color: #64748b;">{{ dup.keyword2_file }}</small>
                            </td>
                            <td style="text-align: center;">
                                <span class="badge-count">{{ dup.similarity_score|round(0)|int }}%</span>
                            </td>
                        </tr>
                        {% endfor %}
                    </tbody>
                </table>
            </div>
            {% endif %}

            <!-- Code Quality Issues -->
            {% if robocop_issues_by_category or robocop_issues_by_severity %}
            <div class="section">
                <div class="section-header">
                    <h2>Code Quality Analysis (Robocop)</h2>
                </div>
                <div class="issue-grid">
                    {% if robocop_issues_by_severity %}
                    <div class="issue-card">
                        <h4>Issues by Severity</h4>
                        {% for severity, count in robocop_issues_by_severity|dictsort(reverse=true) %}
                        <div class="issue-bar">
                            <span class="name"><span class="severity-badge {{ severity }}">{{ severity }}</span></span>
                            <span class="count">{{ count }}</span>
                        </div>
                        {% endfor %}
                    </div>
                    {% endif %}
                    {% if robocop_issues_by_category %}
                    <div class="issue-card">
                        <h4>Issues by Category</h4>
                        {% set max_cat = robocop_issues_by_category.values()|max %}
                        {% set max_count = max_cat if robocop_issues_by_category else 1 %}
                        {% for category, count in robocop_issues_by_category|dictsort %}
                        <div class="issue-bar">
                            <span class="name">{{ category }}</span>
                            <div class="bar">
                                <div class="bar-fill" style="width: {{ (count / max_count * 100)|round(0) }}%"></div>
                            </div>
                            <span class="count">{{ count }}</span>
                        </div>
                        {% endfor %}
                    </div>
                    {% endif %}
                </div>

                {% if risk_files %}
                <div style="margin-top: 25px;">
                    <h3 style="font-size: 1.1em; color: #0f172a; margin-bottom: 15px;">High-Risk Files</h3>
                    <table>
                        <thead>
                            <tr>
                                <th>File Path</th>
                            </tr>
                        </thead>
                        <tbody>
                            {% for file in risk_files %}
                            <tr>
                                <td>{{ file }}</td>
                            </tr>
                            {% endfor %}
                        </tbody>
                    </table>
                </div>
                {% endif %}
            </div>
            {% endif %}

            <!-- File Analysis -->
            {% if files %}
            <div class="section">
                <div class="section-header">
                    <h2>File Analysis</h2>
                    <span class="badge">{{ files|length }} files</span>
                </div>
                <table>
                    <thead>
                        <tr>
                            <th>File Name</th>
                            <th>Type</th>
                            <th style="text-align: center;">Keywords Defined</th>
                            <th style="text-align: center;">Keywords Called</th>
                        </tr>
                    </thead>
                    <tbody>
                        {% for file in files[:30] %}
                        <tr>
                            <td><strong>{{ file.file_name }}</strong></td>
                            <td>{{ 'Resource' if file.is_resource else 'Test' }}</td>
                            <td style="text-align: center;">{{ file.keywords_defined }}</td>
                            <td style="text-align: center;">{{ file.keywords_called }}</td>
                        </tr>
                        {% endfor %}
                        {% if files|length > 30 %}
                        <tr>
                            <td colspan="4" style="text-align: center; color: #64748b; font-style: italic;">
                                ... and {{ files|length - 30 }} more files
                            </td>
                        </tr>
                        {% endif %}
                    </tbody>
                </table>
            </div>
            {% endif %}
        </div>

        <!-- Footer -->
        <div class="footer">
            <div class="brand">RoboView - Robot Framework Keyword Management Tool</div>
            <div class="generated">Report generated on {{ current_date }} using RoboView v{{ roboview_version }}</div>
        </div>
    </div>
</body>
</html>
"""


class HTMLExporter:
    """Exporter for generating HTML reports."""

    @staticmethod
    def export(report: Report, output_path: Path) -> None:
        """Export report to HTML format.

        Arguments:
            report: Report object to export
            output_path: Path where HTML file will be saved

        """
        try:
            output_path.parent.mkdir(parents=True, exist_ok=True)

            # Prepare template context
            context = HTMLExporter._build_context(report)

            # Render template
            template = Template(HTML_TEMPLATE)
            html_content = template.render(**context)

            # Write to HTML file
            with output_path.open("w", encoding="utf-8") as f:
                f.write(html_content)

            logger.info("Report exported to HTML: %s", output_path)

        except Exception:
            logger.exception("Error exporting report to HTML")
            raise

    @staticmethod
    def _build_context(report: Report) -> dict:
        """Build template context from report."""
        context = {
            "title": report.title,
            "project_name": report.metadata.project_name,
            "analysis_date": report.metadata.analysis_date.strftime("%B %d, %Y at %H:%M"),
            "author": report.metadata.author,
            "roboview_version": report.metadata.roboview_version,
            "current_date": datetime.now(UTC).strftime("%B %d, %Y at %H:%M:%S UTC"),
            # KPI data
            "total_keywords": report.summary.total_keywords,
            "unused_keywords": report.summary.unused_keywords,
            "reusage_rate": report.summary.reusage_rate,
            "documentation_coverage": report.summary.documentation_coverage,
            "robocop_issues": report.summary.robocop_issues,
            "total_files": report.summary.total_files,
        }

        # Calculate overall score from KPIs
        kpi = report.summary
        if kpi.total_keywords > 0:
            issue_density = (kpi.robocop_issues / kpi.total_keywords) * 100
            reliability = max(0, 100 - issue_density)
            debt_ratio = (kpi.unused_keywords / kpi.total_keywords) * 100
            technical_debt = max(0, 100 - debt_ratio)
        else:
            reliability = 100
            technical_debt = 100

        overall_score = (
            (kpi.reusage_rate * 0.25)
            + (kpi.documentation_coverage * 0.25)
            + (reliability * 0.25)
            + (technical_debt * 0.25)
        )
        context["overall_score"] = overall_score

        # SummaryReport specific fields
        if isinstance(report, SummaryReport):
            context["risk_level"] = report.risk_level
            context["health_status"] = report.health_status
            context["best_practices_score"] = report.best_practices_score

            # Recommendations
            context["recommendations"] = [
                {
                    "priority": rec.priority,
                    "category": rec.category,
                    "message": rec.message,
                    "details": rec.details,
                }
                for rec in report.recommendations
            ]

            # Most used keywords
            context["most_used_keywords"] = [
                {
                    "keyword_name": kw.keyword_name,
                    "file_name": kw.file_name,
                    "usage_count": kw.usage_count,
                    "documentation": kw.documentation,
                    "line_number": kw.line_number,
                }
                for kw in report.most_used_keywords
            ]

            # Unused keywords
            context["unused_keywords_list"] = [
                {
                    "keyword_name": kw.keyword_name,
                    "file_name": kw.file_name,
                    "line_number": kw.line_number,
                }
                for kw in report.unused_keywords
            ]

            # Undocumented keywords
            context["undocumented_keywords"] = [
                {
                    "keyword_name": kw.keyword_name,
                    "file_name": kw.file_name,
                    "usage_count": kw.usage_count,
                }
                for kw in report.undocumented_keywords
            ]

            # Duplicate keywords
            context["duplicate_keywords"] = [
                {
                    "keyword1_name": dup.keyword1_name,
                    "keyword1_file": dup.keyword1_file,
                    "keyword2_name": dup.keyword2_name,
                    "keyword2_file": dup.keyword2_file,
                    "similarity_score": dup.similarity_score,
                }
                for dup in report.duplicate_keywords
            ]

            # Files
            context["files"] = [
                {
                    "file_name": f.file_name,
                    "file_path": f.file_path,
                    "is_resource": f.is_resource,
                    "keywords_defined": f.keywords_defined,
                    "keywords_called": f.keywords_called,
                }
                for f in report.files
            ]

            # Robocop data
            context["robocop_issues_by_category"] = report.robocop_issues_by_category
            context["robocop_issues_by_severity"] = report.robocop_issues_by_severity
            context["risk_files"] = report.risk_files

        return context
