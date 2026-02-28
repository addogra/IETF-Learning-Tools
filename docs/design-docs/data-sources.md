
# Data Sources

## WG Resolution and Charter
- `https://datatracker.ietf.org/api/v1/group/group/`
- `https://datatracker.ietf.org/wg/<acronym>/about/`

## Drafts
- `https://datatracker.ietf.org/wg/<acronym>/documents/`
- `https://datatracker.ietf.org/doc/draft-.../`
- Optional metadata fallback: `https://datatracker.ietf.org/api/v1/doc/document/`

## Discussions
- `https://mailarchive.ietf.org/arch/browse/<acronym>/`

## Meetings and Agendas
- `https://datatracker.ietf.org/wg/<acronym>/meetings/`
- `https://datatracker.ietf.org/meeting/`
- `https://datatracker.ietf.org/meeting/<number>/`

## Milestones and Document Metadata
- `https://datatracker.ietf.org/api/v1/group/milestone/`
- `https://datatracker.ietf.org/api/v1/doc/document/`

## Notes
- Parsers must tolerate missing sections and changing HTML structure.
- Prefer official API endpoints when available, then degrade to robust HTML parsing.
