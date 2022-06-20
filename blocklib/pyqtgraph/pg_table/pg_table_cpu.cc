/* -*- c++ -*- */
/*
 * Copyright 2022 Josh Morman
 *
 * This file is part of GNU Radio
 *
 * SPDX-License-Identifier: GPL-3.0-or-later
 *
 */

#include "pg_table_cpu.h"
#include "pg_table_cpu_gen.h"

namespace gr {
namespace pyqtgraph {

pg_table_cpu::pg_table_cpu(block_args args) : INHERITED_CONSTRUCTORS {}

work_return_code_t pg_table_cpu::work(std::vector<block_work_input_sptr>& work_input,
                                      std::vector<block_work_output_sptr>& work_output)
{
    // Do <+signal processing+>
    // Block specific code goes here
    return work_return_code_t::WORK_OK;
}


} // namespace pyqtgraph
} // namespace gr