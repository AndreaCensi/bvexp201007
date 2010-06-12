

def create_techreport_figures(reports):
    
    with Latex.document('all.tex') as doc:
        doc.input('vehicles')
    
    with Latex.fragment('vehicles.tex') as f:
        
        figwidth = "3cm"
        
        for report in reports:
            
            f.pagebreak()
            with f.figure(caption=caption) as fig:
                
                fig.hspace()
                with fig.subfigure(caption="") as sub:
                    sub.includegraphics(width=figwidth)  
                fig.hspace()
