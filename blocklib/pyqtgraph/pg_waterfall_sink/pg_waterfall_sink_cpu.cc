/* -*- c++ -*- */
/*
 * Copyright 2022 Josh Morman
 *
 * This file is part of GNU Radio
 *
 * SPDX-License-Identifier: GPL-3.0-or-later
 *
 */

#include "pg_time_sink_cpu.h"
#include "pg_time_sink_cpu_gen.h"

namespace gr {
namespace pyqtgraph {

template <class T>
pg_time_sink_cpu<T>::pg_time_sink_cpu(const typename pg_time_sink<T>::block_args& args)
    : INHERITED_CONSTRUCTORS(T)
{
}

template <class T>
work_return_code_t pg_time_sink_cpu<T>::work(std::vector<block_work_input_sptr>& work_input,
                                         std::vector<block_work_output_sptr>& work_output)
{
    // Do work specific code here
    return work_return_code_t::WORK_OK;
}

} /* namespace pyqtgraph */
} /* namespace gr */
