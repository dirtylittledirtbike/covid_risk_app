# this is the global site tag needed for google analytics
# a lot of this is specific to dash app/a lazy work around

gtag = """<!DOCTYPE html>
            <html>
                <head>
                    <!-- Global site tag (gtag.js) - Google Analytics -->
                    <script async src="https://www.googletagmanager.com/gtag/js?id=UA-177209054-1"></script>
                    <script>
                        window.dataLayer = window.dataLayer || [];
                        function gtag(){dataLayer.push(arguments);}
                        gtag('js', new Date());
                    
                        gtag('config', 'UA-177209054-1');
                    </script>

                    {%metas%}
                    <title>{%title%}</title>
                    {%favicon%}
                    {%css%}
                </head>
                <body>
                    {%app_entry%}
                    <footer>
                        {%config%}
                        {%scripts%}
                        {%renderer%}
                    </footer>
                </body>
            </html>"""
