"""
Command to make HTML files interactive by adding zoom, drag, and other features to diagrams.

This module adds interactive capabilities to SVG diagrams in HTML files:
- Zoom in/out with mouse wheel
- Drag and drop diagrams
- Reset to original size/position with single click
- Visual controls (+/-/Reset buttons)
- Help panel with instructions
"""

import sys
import re
from pathlib import Path
from typing import Optional


# CSS for interactive features
INTERACTIVE_CSS = """<style>
/* Styles pour les fonctionnalités interactives dtk */
.zoom-indicator {
    position: fixed;
    top: 20px;
    right: 20px;
    background-color: rgba(52, 152, 219, 0.9);
    color: white;
    padding: 8px 15px;
    border-radius: 20px;
    font-weight: bold;
    z-index: 1000;
    display: none;
    box-shadow: 0 2px 10px rgba(0,0,0,0.3);
    font-size: 14px;
}

.interaction-help {
    position: fixed;
    bottom: 20px;
    left: 20px;
    background-color: rgba(44, 62, 80, 0.95);
    color: white;
    padding: 15px;
    border-radius: 8px;
    font-size: 12px;
    line-height: 1.4;
    z-index: 1000;
    display: none;
    box-shadow: 0 4px 15px rgba(0,0,0,0.3);
    max-width: 250px;
    opacity: 0;
    transition: opacity 0.3s ease;
}

.interaction-help.visible {
    display: block;
    opacity: 1;
}

.diagram-image.fullscreen {
    position: fixed;
    top: 0;
    left: 0;
    width: 100vw;
    height: 100vh;
    z-index: 999;
    background: rgba(0,0,0,0.9);
    object-fit: contain;
    cursor: zoom-out;
}

.diagram-image {
    transition: transform 0.2s ease, opacity 0.2s ease;
    cursor: grab;
    user-select: none;
    -webkit-user-select: none;
    -moz-user-select: none;
    -ms-user-select: none;
    position: relative;
    z-index: 1;
}

.diagram-block {
    position: relative;
    border: 1px solid #d0d7de;
    border-radius: 6px;
    margin: 16px 0;
    background-color: #f6f8fa;
}

.diagram-block code.diagram-image {
    display: block;
    padding: 16px;
    background-color: #f8f9fa;
    border: 1px solid #e9ecef;
    border-radius: 6px;
    font-family: ui-monospace, SFMono-Regular, "SF Mono", Consolas, "Liberation Mono", Menlo, monospace;
    font-size: 12px;
    line-height: 1.45;
    overflow: auto;
    white-space: pre-wrap;
    word-wrap: break-word;
    color: #212529;
    cursor: grab;
    transition: transform 0.2s ease, opacity 0.2s ease;
}

.diagram-image:active {
    cursor: grabbing;
}

.zoom-controls {
    position: absolute;
    top: 10px;
    right: 10px;
    background-color: rgba(255, 255, 255, 0.9);
    border-radius: 5px;
    padding: 5px;
    z-index: 100;
    box-shadow: 0 2px 5px rgba(0,0,0,0.2);
    display: flex;
    gap: 5px;
}

.zoom-controls button {
    background-color: #3498db;
    color: white;
    border: none;
    border-radius: 3px;
    padding: 5px 10px;
    cursor: pointer;
    font-size: 12px;
    transition: background-color 0.2s;
}

.zoom-controls button:hover {
    background-color: #2980b9;
}

@media print {
    .zoom-indicator, .interaction-help, .zoom-controls {
        display: none !important;
    }
}
</style>"""


# JavaScript for interactive features
INTERACTIVE_JS = """<script>
document.addEventListener('DOMContentLoaded', function() {
    console.log('=== Fonctionnalités interactives chargées ===');

    const enabledFeatures = {
        zoom: true,
        drag: true,
        fullscreen: true,
        help: true,
        controls: true
    };

    // Sélectionner tous les SVG
    const svgElements = document.querySelectorAll('svg');
    console.log('SVG trouvés:', svgElements.length);

    const allInteractiveElements = Array.from(svgElements);

    // Ajouter la classe diagram-image
    allInteractiveElements.forEach(svg => {
        if (!svg.classList.contains('diagram-image')) {
            svg.classList.add('diagram-image');
        }
    });

    let zoomIndicator = null;
    let helpPanel = null;

    // Créer l'indicateur de zoom
    function createZoomIndicator() {
        zoomIndicator = document.createElement('div');
        zoomIndicator.className = 'zoom-indicator';
        document.body.appendChild(zoomIndicator);
    }

    // Créer le panneau d'aide
    function createHelpPanel() {
        if (!enabledFeatures.help) return;

        helpPanel = document.createElement('div');
        helpPanel.className = 'interaction-help';

        let helpContent = '<strong>Contrôles diagramme:</strong><br>';
        if (enabledFeatures.zoom) helpContent += '• Molette: Zoom/Dézoom<br>';
        if (enabledFeatures.drag) helpContent += '• Clic + glisser: Déplacer<br>';
        if (enabledFeatures.drag) helpContent += '• Clic simple: Réinitialiser<br>';
        if (enabledFeatures.fullscreen) helpContent += '• F/Entrée/Espace: Plein écran<br>';
        if (enabledFeatures.fullscreen) helpContent += '• Échap: Quitter plein écran<br>';

        helpPanel.innerHTML = helpContent;
        document.body.appendChild(helpPanel);
    }

    // Mettre à jour l'indicateur de zoom
    function updateZoomIndicator(scale, visible = true) {
        if (!zoomIndicator) createZoomIndicator();
        zoomIndicator.textContent = 'Zoom: ' + Math.round(scale * 100) + '%';
        zoomIndicator.style.display = visible ? 'block' : 'none';
    }

    // Afficher/masquer l'aide
    function toggleHelp(show) {
        if (!helpPanel) createHelpPanel();
        helpPanel.classList.toggle('visible', show);
    }

    allInteractiveElements.forEach((img, index) => {
        let scale = 1;
        let isDragging = false;
        let hasMoved = false;
        let startX, startY, translateX = 0, translateY = 0;
        let isFullscreen = false;
        let helpTimeout = null;
        let currentZIndex = 1;

        function updateTransform() {
            img.style.transform = 'translate(' + translateX + 'px, ' + translateY + 'px) scale(' + scale + ')';
        }

        // Zoom avec molette
        if (enabledFeatures.zoom) {
            img.addEventListener('wheel', function(e) {
                e.preventDefault();
                const delta = e.deltaY > 0 ? -0.1 : 0.1;
                scale = Math.max(0.5, Math.min(5, scale + delta));
                updateTransform();

                if (isFullscreen) {
                    updateZoomIndicator(scale);
                }
            });
        }

        // Drag and drop
        if (enabledFeatures.drag) {
            img.addEventListener('mousedown', function(e) {
                e.preventDefault();
                isDragging = true;
                hasMoved = false;
                startX = e.clientX - translateX;
                startY = e.clientY - translateY;
                img.style.cursor = 'grabbing';
                img.style.opacity = '0.7';
                currentZIndex++;
                img.style.zIndex = currentZIndex.toString();
            });

            document.addEventListener('mousemove', function(e) {
                if (isDragging) {
                    hasMoved = true;
                    translateX = e.clientX - startX;
                    translateY = e.clientY - startY;
                    updateTransform();
                }
            });

            document.addEventListener('mouseup', function(e) {
                if (isDragging) {
                    isDragging = false;
                    img.style.cursor = 'grab';
                    img.style.opacity = '1';
                }
            });
        }

        // Reset avec clic simple (seulement si pas de mouvement)
        if (enabledFeatures.drag || enabledFeatures.zoom) {
            img.addEventListener('click', function(e) {
                e.preventDefault();

                if (hasMoved) {
                    hasMoved = false;
                    return;
                }

                // Réinitialiser
                scale = 1;
                translateX = 0;
                translateY = 0;
                updateTransform();

                if (isFullscreen) {
                    updateZoomIndicator(scale);
                }
            });
        }

        // Mode plein écran
        if (enabledFeatures.fullscreen) {
            document.addEventListener('keydown', function(e) {
                if (img.matches(':hover') || isFullscreen) {
                    switch(e.key) {
                        case 'Escape':
                            if (isFullscreen) {
                                isFullscreen = false;
                                img.classList.remove('fullscreen');
                                updateZoomIndicator(scale, false);
                                toggleHelp(false);
                            }
                            break;
                        case 'f':
                        case 'F':
                        case 'Enter':
                        case ' ':
                            isFullscreen = !isFullscreen;
                            img.classList.toggle('fullscreen', isFullscreen);
                            if (isFullscreen) {
                                updateZoomIndicator(scale);
                                toggleHelp(true);
                            } else {
                                updateZoomIndicator(scale, false);
                                toggleHelp(false);
                            }
                            break;
                        case '+':
                        case '=':
                            scale = Math.min(5, scale + 0.2);
                            updateTransform();
                            if (isFullscreen) updateZoomIndicator(scale);
                            break;
                        case '-':
                            scale = Math.max(0.5, scale - 0.2);
                            updateTransform();
                            if (isFullscreen) updateZoomIndicator(scale);
                            break;
                        case '0':
                            scale = 1;
                            translateX = 0;
                            translateY = 0;
                            updateTransform();
                            if (isFullscreen) updateZoomIndicator(scale);
                            break;
                    }
                }
            });
        }

        // Afficher l'aide au survol
        if (enabledFeatures.help) {
            img.addEventListener('mouseenter', function() {
                if (helpTimeout) clearTimeout(helpTimeout);
                helpTimeout = setTimeout(function() { toggleHelp(true); }, 1000);
            });

            img.addEventListener('mouseleave', function() {
                if (helpTimeout) clearTimeout(helpTimeout);
                if (!isFullscreen) {
                    toggleHelp(false);
                }
            });
        }

        // Ajouter des contrôles visuels
        if (enabledFeatures.controls && (enabledFeatures.zoom || enabledFeatures.drag)) {
            const container = img.closest('.diagram, .diagram-container') || img.parentElement;

            if (container && !container.querySelector('.zoom-controls')) {
                const controls = document.createElement('div');
                controls.className = 'zoom-controls';

                let controlsHTML = '';
                if (enabledFeatures.zoom) {
                    controlsHTML += '<button class=\"zoom-in\" title=\"Zoom avant\">+</button>';
                    controlsHTML += '<button class=\"zoom-out\" title=\"Zoom arrière\">-</button>';
                }
                if (enabledFeatures.zoom || enabledFeatures.drag) {
                    controlsHTML += '<button class=\"reset\" title=\"Réinitialiser\">Reset</button>';
                }

                controls.innerHTML = controlsHTML;
                container.style.position = 'relative';
                container.appendChild(controls);

                const zoomInBtn = controls.querySelector('.zoom-in');
                const zoomOutBtn = controls.querySelector('.zoom-out');
                const resetBtn = controls.querySelector('.reset');

                if (zoomInBtn) {
                    zoomInBtn.addEventListener('click', function(e) {
                        e.stopPropagation();
                        scale = Math.min(5, scale + 0.2);
                        updateTransform();
                        if (isFullscreen) updateZoomIndicator(scale);
                    });
                }

                if (zoomOutBtn) {
                    zoomOutBtn.addEventListener('click', function(e) {
                        e.stopPropagation();
                        scale = Math.max(0.5, scale - 0.2);
                        updateTransform();
                        if (isFullscreen) updateZoomIndicator(scale);
                    });
                }

                if (resetBtn) {
                    resetBtn.addEventListener('click', function(e) {
                        e.stopPropagation();
                        scale = 1;
                        translateX = 0;
                        translateY = 0;
                        updateTransform();
                        if (isFullscreen) updateZoomIndicator(scale);
                    });
                }
            }
        }
    });

    console.log('=== Setup terminé ===');
});
</script>"""


def make_html_interactive(
    input_path: str,
    output_path: Optional[str] = None,
    verbose: bool = False
) -> int:
    """
    Make an HTML file interactive by adding zoom and drag capabilities to diagrams.

    Args:
        input_path: Path to input HTML file
        output_path: Optional path to output HTML file. If None, adds .interactive before extension
        verbose: Print detailed progress

    Returns:
        Exit code (0 for success, 1 for error)
    """
    input_file = Path(input_path).resolve()

    # Check if input file exists
    if not input_file.exists():
        print(f"Error: Input file '{input_path}' does not exist.", file=sys.stderr)
        return 1

    if not input_file.is_file():
        print(f"Error: '{input_path}' is not a file.", file=sys.stderr)
        return 1

    # Determine output path
    if output_path is None:
        output_file = input_file.parent / f"{input_file.stem}.interactive{input_file.suffix}"
    else:
        output_file = Path(output_path).resolve()

    if verbose:
        print(f"Processing: {input_file}")
        print(f"Output: {output_file}")

    try:
        # Read HTML content
        with open(input_file, 'r', encoding='utf-8') as f:
            html_content = f.read()

        if verbose:
            print(f"HTML file size: {len(html_content):,} bytes")

        # Check for SVG elements
        svg_count = html_content.count('<svg')
        if verbose:
            print(f"SVG diagrams found: {svg_count}")

        if svg_count == 0:
            print("Warning: No SVG diagrams found in the HTML file.", file=sys.stderr)
            print("The interactive features work with SVG diagrams.", file=sys.stderr)

        # Inject CSS before </head>
        if '</head>' in html_content:
            html_content = html_content.replace('</head>', INTERACTIVE_CSS + '\n</head>', 1)
            if verbose:
                print("CSS injected before </head>")
        else:
            print("Warning: No </head> tag found. CSS will be added at the beginning.", file=sys.stderr)
            html_content = INTERACTIVE_CSS + '\n' + html_content

        # Inject JavaScript before </body>
        if '</body>' in html_content:
            html_content = html_content.replace('</body>', INTERACTIVE_JS + '\n</body>', 1)
            if verbose:
                print("JavaScript injected before </body>")
        else:
            print("Warning: No </body> tag found. JavaScript will be added at the end.", file=sys.stderr)
            html_content = html_content + '\n' + INTERACTIVE_JS

        # Write output file
        with open(output_file, 'w', encoding='utf-8') as f:
            f.write(html_content)

        print(f"\n[SUCCESS] Interactive HTML created: {output_file}")
        print(f"[INFO] File size: {len(html_content):,} bytes")
        if svg_count > 0:
            print(f"[INFO] {svg_count} SVG diagram(s) are now interactive")
            print(f"[INFO] Features: Zoom (mouse wheel), Drag (click+drag), Reset (click)")
        else:
            print(f"[INFO] No SVG diagrams found - interactive features may not work")

        return 0

    except Exception as e:
        print(f"Error: Failed to make HTML interactive: {e}", file=sys.stderr)
        import traceback
        if verbose:
            traceback.print_exc()
        return 1


def register_make_interactive_command(subparsers):
    """
    Register the make-interactive command with the argument parser.

    Args:
        subparsers: The subparsers object from argparse
    """
    parser = subparsers.add_parser(
        'make-interactive',
        help='Make HTML diagrams interactive with zoom and drag',
        description='Add interactive capabilities to SVG diagrams in HTML files. '
                    'Enables zoom (mouse wheel), drag and drop, and visual controls.'
    )

    parser.add_argument(
        'input',
        type=str,
        help='HTML file to make interactive'
    )

    parser.add_argument(
        '-o', '--output',
        type=str,
        default=None,
        help='Output HTML file path (default: <input>.interactive.html)'
    )

    parser.add_argument(
        '--verbose',
        action='store_true',
        help='Show detailed progress'
    )

    parser.set_defaults(func=lambda args: make_html_interactive(
        args.input,
        args.output,
        args.verbose
    ))
