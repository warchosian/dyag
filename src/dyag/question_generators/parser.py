"""
Parser for structured Markdown documents containing application information
"""

import re
from dataclasses import dataclass, field
from typing import List, Dict, Optional
from pathlib import Path


@dataclass
class Application:
    """Represents an application extracted from Markdown"""

    name: str
    full_name: Optional[str] = None
    app_id: Optional[str] = None
    status: Optional[str] = None
    geographic_scope: Optional[str] = None
    description: Optional[str] = None
    domains: List[str] = field(default_factory=list)
    websites: List[str] = field(default_factory=list)
    events: List[Dict[str, str]] = field(default_factory=list)
    actors: List[str] = field(default_factory=list)
    contacts: List[str] = field(default_factory=list)
    related_data: List[str] = field(default_factory=list)
    related_apps: List[Dict[str, str]] = field(default_factory=list)
    metadata: Dict[str, str] = field(default_factory=dict)
    raw_content: str = ""

    def to_dict(self) -> Dict:
        """Convert to dictionary"""
        return {
            "name": self.name,
            "full_name": self.full_name,
            "app_id": self.app_id,
            "status": self.status,
            "geographic_scope": self.geographic_scope,
            "description": self.description,
            "domains": self.domains,
            "websites": self.websites,
            "events": self.events,
            "actors": self.actors,
            "contacts": self.contacts,
            "related_data": self.related_data,
            "related_apps": self.related_apps,
            "metadata": self.metadata,
        }


class MarkdownParser:
    """Parser for structured Markdown application documents"""

    def __init__(self, verbose: bool = False):
        self.verbose = verbose

    def parse_file(self, file_path: str) -> List[Application]:
        """Parse a Markdown file and extract applications"""
        content = Path(file_path).read_text(encoding='utf-8')
        return self.parse_content(content)

    def parse_content(self, content: str) -> List[Application]:
        """Parse Markdown content and extract applications"""
        applications = []

        # Split by top-level headers (# Application Name)
        # Skip the first section (document header)
        sections = re.split(r'\n# ([^\n]+)\n', content)

        # sections[0] is the header before first #
        # sections[1::2] are the app names
        # sections[2::2] are the app contents

        if len(sections) < 3:
            if self.verbose:
                print(f"[WARNING] No applications found in document")
            return applications

        app_names = sections[1::2]
        app_contents = sections[2::2]

        for name, app_content in zip(app_names, app_contents):
            if self.verbose:
                print(f"[PARSE] Extracting application: {name}")

            app = self._parse_application(name.strip(), app_content)
            applications.append(app)

        if self.verbose:
            print(f"[OK] Extracted {len(applications)} applications")

        return applications

    def _parse_application(self, name: str, content: str) -> Application:
        """Parse a single application section"""
        app = Application(name=name, raw_content=content)

        lines = content.split('\n')
        current_section = None
        section_content = []

        for line in lines:
            # Check for ## headers (sections)
            if line.startswith('##'):
                # Save previous section
                if current_section and section_content:
                    self._process_section(app, current_section, section_content)

                # Start new section
                current_section = line.lstrip('#').strip()
                section_content = []

            # Check for metadata fields (**Field:** value)
            elif line.startswith('**') and ':' in line:
                field, value = self._extract_field(line)
                if field and value:
                    self._set_field(app, field, value)

            else:
                # Accumulate section content
                if current_section:
                    section_content.append(line)

        # Process last section
        if current_section and section_content:
            self._process_section(app, current_section, section_content)

        return app

    def _extract_field(self, line: str) -> tuple:
        """Extract field name and value from **Field:** value format"""
        match = re.match(r'\*\*([^:*]+):\*\*\s*(.+)', line)
        if match:
            field = match.group(1).strip()
            value = match.group(2).strip()
            return field, value
        return None, None

    def _set_field(self, app: Application, field: str, value: str):
        """Set application field based on field name"""
        field_lower = field.lower()

        if 'nom complet' in field_lower or 'full name' in field_lower:
            app.full_name = value
        elif field_lower == 'id':
            app.app_id = value
        elif 'statut' in field_lower or 'status' in field_lower:
            app.status = value
        elif 'portée' in field_lower or 'géographique' in field_lower or 'scope' in field_lower:
            app.geographic_scope = value
        elif 'modification' in field_lower:
            app.metadata['modification'] = value
        else:
            # Store in metadata
            app.metadata[field] = value

    def _process_section(self, app: Application, section_name: str, content: List[str]):
        """Process a section and extract relevant information"""
        section_lower = section_name.lower()
        text = '\n'.join(content).strip()

        if 'description' in section_lower:
            app.description = text

        elif 'domaine' in section_lower and 'métier' in section_lower:
            # Extract list items
            app.domains = self._extract_list_items(content)

        elif 'site' in section_lower and 'web' in section_lower:
            # Extract URLs
            app.websites = self._extract_urls(content)

        elif 'événement' in section_lower or 'event' in section_lower:
            # Extract events with dates
            app.events = self._extract_events(content)

        elif 'acteur' in section_lower or 'actor' in section_lower:
            app.actors = self._extract_list_items(content)

        elif 'contact' in section_lower:
            app.contacts = self._extract_contacts(content)

        elif 'données liées' in section_lower or 'related data' in section_lower:
            app.related_data = self._extract_list_items(content)

        elif 'applications liées' in section_lower or 'related app' in section_lower:
            app.related_apps = self._extract_related_apps(content)

    def _extract_list_items(self, lines: List[str]) -> List[str]:
        """Extract items from a list (- item format)"""
        items = []
        for line in lines:
            line = line.strip()
            if line.startswith('- '):
                item = line[2:].strip()
                if item:
                    items.append(item)
        return items

    def _extract_urls(self, lines: List[str]) -> List[str]:
        """Extract URLs from markdown links"""
        urls = []
        for line in lines:
            # Match [text](url) format
            matches = re.findall(r'\[([^\]]+)\]\(([^\)]+)\)', line)
            for text, url in matches:
                urls.append(url)
        return urls

    def _extract_events(self, lines: List[str]) -> List[Dict[str, str]]:
        """Extract events with dates"""
        events = []
        for line in lines:
            line = line.strip()
            if line.startswith('- **'):
                # Format: - **DD/MM/YYYY** : Event description
                match = re.match(r'-\s*\*\*([^*]+)\*\*\s*:\s*(.+)', line)
                if match:
                    date = match.group(1).strip()
                    description = match.group(2).strip()
                    events.append({"date": date, "description": description})
        return events

    def _extract_contacts(self, lines: List[str]) -> List[str]:
        """Extract contact information"""
        contacts = []
        for line in lines:
            line = line.strip()
            if line.startswith('- '):
                contact = line[2:].strip()
                if contact:
                    contacts.append(contact)
        return contacts

    def _extract_related_apps(self, lines: List[str]) -> List[Dict[str, str]]:
        """Extract related applications"""
        apps = []
        for line in lines:
            line = line.strip()
            if line.startswith('- **'):
                # Format: - **AppName** (ID: 123)
                match = re.match(r'-\s*\*\*([^*]+)\*\*\s*\(ID:\s*(\d+)\)', line)
                if match:
                    name = match.group(1).strip()
                    app_id = match.group(2).strip()
                    apps.append({"name": name, "id": app_id})
        return apps
