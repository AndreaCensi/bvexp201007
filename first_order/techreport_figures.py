from reprep.out.platex import Latex, latexify, makeupcmd, safecmd
import os

    

def graphics(sub, node, width, border=True):
    if border:
        sub.tex('\\setlength\\fboxsep{0pt}\\fbox{')
    sub.graphics_data(node.raw_data, node.mime, width=width, id=node.get_complete_id())
    
    if border:
        sub.tex('}')
    
def create_techreport_figures(directory, reports):
    
    short = ['v_olfaction360o', 'v_optic_unif', 'v_rangefinder180_center']

    all =  short+ ['v_optic_nonunif', 'v_rangefinder_unif', 
                     'v_rangefinder_nonunif',  'v_rangefinder180_left30',
                      'v_rangefinder180_front30', 'v_rangefinder180_rot45', 
                      'v_olfaction180o', 'v_olfaction180n', 
                      'v_olfaction360n'] # 'v_polarized']


    create_techreport_figures_sub(reports, directory, "", short)
    create_techreport_figures_sub(reports, directory, "extended_", all)
    
    
    
def create_techreport_figures_sub(reports, directory, prefix, use_vehicles):
    if not os.path.exists(directory):
        os.makedirs(directory)
        
    # create dict vname -> report
    all_vehicles = dict([(report.id, report) for report in reports])
    not_used = set(all_vehicles.keys()).difference(set(use_vehicles))
    print "Vehicles not used: %s" % list(not_used)
    
    success_file = '%ssuccess.tex' % prefix
    tensors_file = '%stensors.tex' % prefix
    covariance_file = '%scovariance.tex' % prefix
    
    all_figures = os.path.join(directory, '%sall_figures.tex' % prefix)
    W = "1.7cm"
    interspace="2mm"
    padding="2.5mm"
    
    with Latex.document(all_figures, document_class='svmult') as doc:
        #doc.use_package('fullpage')
        #doc.input('vehicles_covariance')    
        #doc.tex('\\clearpage')
        doc.input(tensors_file)
        doc.tex('\\clearpage')
        doc.input(success_file)
        
    vehicles_covariance = os.path.join(directory, covariance_file)
    with Latex.fragment(vehicles_covariance, graphics_path=directory) as frag:
        for vname in use_vehicles:
            report = all_vehicles[vname]
            
            icon = report.resolve_url('vehicle-icon/icon')
            covfig = report.resolve_url('covariance/posneg')
            corrfig = report.resolve_url('correlation/posneg')
            inffig =  report.resolve_url('information/posneg')
            # TODO: add information
            label = "%s:covariance" % vname
            frag.pagebreak()
            with frag.figure(label=label, caption=latexify(vname)) as fig:
                fig.hfill()
                with fig.subfigure(caption="Robot") as sub:
                    graphics(sub, icon, W,border=False)
                fig.hfill()
                with fig.subfigure(caption="Covariance matrix") as sub:
                    graphics(sub, covfig, W)
                fig.hfill()
                with fig.subfigure(caption="Correlation matrix") as sub:
                    graphics(sub, corrfig, W)
                with fig.subfigure(caption="Information matrix") as sub:
                    graphics(sub, inffig, W)
                fig.hfill()

    learned_tensors = os.path.join(directory, tensors_file)
    with Latex.fragment(learned_tensors, graphics_path=directory) as frag:

        frag.tex( makeupcmd("Mcov") )
        frag.tex( makeupcmd("Minf") )
        frag.tex( makeupcmd("Txnat") )
        frag.tex( makeupcmd("Tynat") )
        frag.tex( makeupcmd("Tthetanat") )
        frag.tex( makeupcmd("Txnorm") )
        frag.tex( makeupcmd("Tynorm") )
        frag.tex( makeupcmd("Tthetanorm") )
        

        for vname in use_vehicles:
            report = all_vehicles[vname]
            
            icon = report.resolve_url('vehicle-icon/icon')
            
            covfig = report.resolve_url('covariance/posneg')
            inffig =  report.resolve_url('information/posneg')
       
            Tx_nat = report.resolve_url('tensors-natural/tensors/Tx/posneg')
            Ty_nat = report.resolve_url('tensors-natural/tensors/Ty/posneg')
            Ttheta_nat = report.resolve_url('tensors-natural/tensors/Ttheta/posneg')
            
            Tx_norm = report.resolve_url('tensors-normalized/tensors/Tx/posneg')
            Ty_norm = report.resolve_url('tensors-normalized/tensors/Ty/posneg')
            Ttheta_norm = report.resolve_url('tensors-normalized/tensors/Ttheta/posneg')
             
            # TODO: add information
        
            captioncmd = "%sCAPTIONTENS" % safecmd(vname)
            frag.tex( makeupcmd(captioncmd) )
            label = "%s:tensors" % vname
            
            with frag.figure(label=label, caption="\\%s"%captioncmd, placement="p") as fig:
                fig.hfill()
                with fig.subfigure(caption="Robot") as sub:
                    graphics(sub, icon, W, border=False)
                fig.hfill()
                
                with fig.subfigure(caption="\\Txnat") as sub:
                    sub.hspace(padding)
                    graphics(sub, Tx_nat, W)
                    sub.hspace(padding)
                fig.hspace(interspace)
                with fig.subfigure(caption="\\Tynat") as sub:
                    sub.hspace(padding)
                    graphics(sub, Ty_nat, W)
                    sub.hspace(padding)
                fig.hspace(interspace)
                with fig.subfigure(caption="\\Tthetanat") as sub:
                    sub.hspace(padding)
                    graphics(sub, Ttheta_nat, W)
                    sub.hspace(padding)
                
                # I don't know why it makes things uneven
                #fig.hspace(interspace)
                
                fig.parbreak()
            
                
                fig.hfill()
                fig.hspace("-4mm")
                with fig.subfigure(caption="\\Mcov") as sub:
                    graphics(sub, covfig, W)
                fig.hspace(interspace)
                with fig.subfigure(caption="\\Minf") as sub:
                    graphics(sub, inffig, W)
                
                fig.hfill()
                
                
                with fig.subfigure(caption="\\Txnorm") as sub:
                    sub.hspace(padding)
                    graphics(sub, Tx_norm, W)
                    sub.hspace(padding)
                fig.hspace(interspace)
                with fig.subfigure(caption="\\Tynorm") as sub:
                    sub.hspace(padding)
                    graphics(sub, Ty_norm, W)
                    sub.hspace(padding)
                fig.hspace(interspace)
                with fig.subfigure(caption="\\Tthetanorm") as sub:
                    sub.hspace(padding)
                    graphics(sub, Ttheta_norm, W)
                    sub.hspace(padding)
                fig.hspace(interspace)
                
    success = os.path.join(directory, success_file)
    with Latex.fragment(success, graphics_path=directory) as frag:
        
        frag.tex( makeupcmd("sxynat") )
        frag.tex( makeupcmd("sytnat") )
        frag.tex( makeupcmd("sxtnat") )
        
        frag.tex( makeupcmd("sxynorm") )
        frag.tex( makeupcmd("sytnorm") )
        frag.tex( makeupcmd("sxtnorm") )
        
        
        frag.tex( makeupcmd("sucfigA") )
        frag.tex( makeupcmd("sucfigB") )
        frag.tex( makeupcmd("sucfigC") )
        
        for i, vname in enumerate(use_vehicles):
            report = all_vehicles[vname]
                    
            icon = report.resolve_url('vehicle-icon/icon')
            
            succ_xy_nat = report.resolve_url('fields-natural/success-x_y/success')
            succ_yt_nat = report.resolve_url('fields-natural/success-theta_y/success')
            succ_xt_nat = report.resolve_url('fields-natural/success-x_theta/success')
            succ_xy_norm = report.resolve_url('fields-normalized/success-x_y/success')
            succ_yt_norm = report.resolve_url('fields-normalized/success-theta_y/success')
            succ_xt_norm = report.resolve_url('fields-normalized/success-x_theta/success')
             
            # TODO: add information
            label = "%s:success" % vname
        
            captioncmd = "%sCAPTIONSUCC" % safecmd(vname)
            frag.tex( makeupcmd(captioncmd) )
            label = "%s:success" % vname
            
            with frag.figure(label=label, caption="\\%s"%captioncmd, placement="p") as fig:
                fig.hfill()
                #with fig.subfigure(caption="Robot") as sub:
                graphics(fig, icon, W, border=False)
                fig.hfill()
                
                with fig.subfigure(caption="\\sxynat") as sub:
                    sub.hspace(padding)
                    graphics(sub, succ_xy_nat, W)
                    sub.hspace(padding)
                fig.hspace(interspace)
                with fig.subfigure(caption="\\sytnat") as sub:
                    sub.hspace(padding)
                    graphics(sub, succ_yt_nat, W)
                    sub.hspace(padding)
                fig.hspace(interspace)
                with fig.subfigure(caption="\\sxtnat") as sub:
                    sub.hspace(padding)
                    graphics(sub, succ_xt_nat, W)
                    sub.hspace(padding)
                #fig.hspace(interspace)
                
                fig.parbreak()
                fig.hfill()
                
                letter = ['A','B','C']
                fig.tex('\\sucfig%s' % letter[i % 3])
                
                with fig.subfigure(caption="\\sxynorm") as sub:
                    sub.hspace(padding)
                    graphics(sub, succ_xy_norm, W)
                    sub.hspace(padding)
                fig.hspace(interspace)
                with fig.subfigure(caption="\\sytnorm") as sub:
                    sub.hspace(padding)
                    graphics(sub, succ_yt_norm, W)
                    sub.hspace(padding)
                fig.hspace(interspace)
                with fig.subfigure(caption="\\sxtnorm") as sub:
                    sub.hspace(padding)
                    graphics(sub, succ_xt_norm, W)
                    sub.hspace(padding)
                fig.hspace(interspace)
         
                #if i % 3 == 2:
                #   fig.vspace("-1cm")




