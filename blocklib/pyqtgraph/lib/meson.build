pyqtgraph_sources += []
pyqtgraph_deps += [gnuradio_gr_dep, volk_dep, fmt_dep, pmtf_dep, python3_embed_dep, json_dep]

block_cpp_args = ['-DHAVE_CPU']

incdir = include_directories(['../include/gnuradio/pyqtgraph','../include'])
gnuradio_blocklib_pyqtgraph_lib = library('gnuradio-blocklib-pyqtgraph', 
    pyqtgraph_sources, 
    include_directories : incdir, 
    install : true,
    link_language: 'cpp',
    dependencies : pyqtgraph_deps,
    link_args : ['-lgnuradio-runtime'],
    cpp_args : block_cpp_args)

gnuradio_blocklib_pyqtgraph_dep = declare_dependency(include_directories : incdir,
					   link_with : gnuradio_blocklib_pyqtgraph_lib,
                       dependencies : pyqtgraph_deps)
