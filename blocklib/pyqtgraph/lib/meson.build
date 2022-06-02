pyqtgraph_sources += []
pyqtgraph_deps += [gnuradio_gr_dep, volk_dep, fmt_dep, pmtf_dep, python3_embed_dep]

block_cpp_args = ['-DHAVE_CPU']

# if cuda_dep.found() and get_option('enable_cuda')
#     block_cpp_args += '-DHAVE_CUDA'

#     gnuradio_blocklib_pyqtgraph_cu = library('gnuradio-blocklib-pyqtgraph-cu', 
#         pyqtgraph_cu_sources, 
#         include_directories : incdir, 
#         install : true, 
#         dependencies : [cuda_dep])

#     gnuradio_blocklib_pyqtgraph_cu_dep = declare_dependency(include_directories : incdir,
#                         link_with : gnuradio_blocklib_pyqtgraph_cu,
#                         dependencies : cuda_dep)

#     pyqtgraph_deps += [gnuradio_blocklib_pyqtgraph_cu_dep, cuda_dep]

# endif

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
