from reprep.out.platex import Latex, latexify
import os


def graphics(sub, node, width):
    sub.graphics_data(node.raw_data, node.mime, width=width, id=node.get_complete_id())

def create_techreport_figures(directory, reports):
    if not os.path.exists(directory):
        os.makedirs(directory)
        
    # create dict vname -> report
    all_vehicles = dict([(report.id, report) for report in reports])
    
    use_vehicles =  ['v_optic_unif', 'v_optic_nonunif', 'v_rangefinder_unif', 
                     'v_rangefinder_nonunif', 
                     'v_rangefinder180_center', 'v_rangefinder180_left30',
                      'v_rangefinder180_front30', 'v_rangefinder180_rot45', 
                      'v_olfaction180o', 'v_olfaction180n', 'v_olfaction360o', 
                      'v_olfaction360n', 'v_polarized']

    not_used = set(all_vehicles.keys()).difference(set(use_vehicles))
    print "Vehicles not used: %s" % list(not_used)
    
        
    all_figures = os.path.join(directory, 'all_figures.tex')
    W = "2.3cm"
    
    with Latex.document(all_figures) as doc:
        doc.use_package('fullpage')
        doc.input('vehicles_covariance')    
        doc.tex('\\clearpage')
        doc.input('learned_tensors')
        doc.tex('\\clearpage')
        doc.input('success')
        
    vehicles_covariance = os.path.join(directory, 'vehicles_covariance.tex')
    with Latex.fragment(vehicles_covariance, graphics_path=directory) as frag:
        for vname in use_vehicles:
            report = all_vehicles[vname]
            
            icon = report.resolve_url('vehicle-icon/icon')
            covfig = report.resolve_url('covariance/posneg')
            corrfig = report.resolve_url('correlation/posneg')
            # TODO: add information
            label = "%s:covariance" % vname
            frag.pagebreak()
            with frag.figure(label=label, caption=latexify(vname)) as fig:
                fig.hfill()
                with fig.subfigure(caption="Configuration") as sub:
                    graphics(sub, icon, W)
                fig.hfill()
                with fig.subfigure(caption="Covariance matrix") as sub:
                    graphics(sub, covfig, W)
                fig.hfill()
                with fig.subfigure(caption="Correlation matrix") as sub:
                    graphics(sub, corrfig, W)
                fig.hfill()

    learned_tensors = os.path.join(directory, 'learned_tensors.tex')
    with Latex.fragment(learned_tensors, graphics_path=directory) as frag:
        for vname in use_vehicles:
            report = all_vehicles[vname]
            
            icon = report.resolve_url('vehicle-icon/icon')
            
            Tx_nat = report.resolve_url('tensors-natural/tensors/Tx/posneg')
            Ty_nat = report.resolve_url('tensors-natural/tensors/Ty/posneg')
            Ttheta_nat = report.resolve_url('tensors-natural/tensors/Ttheta/posneg')
            
            Tx_norm = report.resolve_url('tensors-normalized/tensors/Tx/posneg')
            Ty_norm = report.resolve_url('tensors-normalized/tensors/Ty/posneg')
            Ttheta_norm = report.resolve_url('tensors-normalized/tensors/Ttheta/posneg')
             
            # TODO: add information
            label = "%s:tensors" % vname
            
            with frag.figure(label=label, caption=latexify(vname)) as fig:
                with fig.subfigure(caption="Configuration") as sub:
                    graphics(sub, icon, W)
                fig.hfill()
                with fig.subfigure(caption="$T_x$") as sub:
                    graphics(sub, Tx_nat, W)
                fig.hfill()
                with fig.subfigure(caption="$T_y$") as sub:
                    graphics(sub, Ty_nat, W)
                fig.hfill()
                with fig.subfigure(caption="$T_\\theta$") as sub:
                    graphics(sub, Ttheta_nat, W)
                fig.hfill()
                
                fig.parbreak()
                fig.hfill()
                
                with fig.subfigure(caption="$T_x$ (norm)") as sub:
                    graphics(sub, Tx_norm, W)
                fig.hfill()
                with fig.subfigure(caption="$T_y$ (norm)") as sub:
                    graphics(sub, Ty_norm, W)
                fig.hfill()
                with fig.subfigure(caption="$T_\\theta$ (norm)") as sub:
                    graphics(sub, Ttheta_norm, W)
                fig.hfill()
                
    success = os.path.join(directory, 'success.tex')
    with Latex.fragment(success, graphics_path=directory) as frag:
        for vname in use_vehicles:
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
            
            with frag.figure(label=label, caption=latexify(vname)) as fig:
                with fig.subfigure(caption="Configuration") as sub:
                    graphics(sub, icon, W)
                fig.hfill()
                with fig.subfigure(caption="$x,y$") as sub:
                    graphics(sub, succ_xy_nat, W)
                fig.hfill()
                with fig.subfigure(caption="$y,\\theta$") as sub:
                    graphics(sub, succ_yt_nat, W)
                fig.hfill()
                with fig.subfigure(caption="$x,\\theta$") as sub:
                    graphics(sub, succ_xt_nat, W)
                fig.hfill()
                
                fig.parbreak()
                fig.hfill()
                
                with fig.subfigure(caption="$x,y$") as sub:
                    graphics(sub, succ_xy_norm, W)
                fig.hfill()
                with fig.subfigure(caption="$y,\\theta$") as sub:
                    graphics(sub, succ_yt_norm, W)
                fig.hfill()
                with fig.subfigure(caption="$x,\\theta$") as sub:
                    graphics(sub, succ_xt_norm, W)
                fig.hfill()
     
                




